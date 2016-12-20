#!/usr/bin/env python3

import configparser
import os
import sqlite3

import numpy as np
import pandas as pd
import pycountry


def main():
    config = configparser.ConfigParser()
    config.read("stacktrends.ini")

    # Read in all tables
    con = sqlite3.connect(config["Database"]["filename"])
    locations = pd.read_sql_query("SELECT * FROM locations", con)
    users = pd.read_sql_query("SELECT * FROM users", con, "Id")
    posts = pd.read_sql_query("SELECT * FROM posts", con, "Id",
                              parse_dates=["CreationDate"])
    con.close()

    #
    # Prepare data
    #

    users = merge_users_countries(users, locations)
    posts = merge_posts_countries(posts, users)

    posts["year"] = posts["CreationDate"].dt.strftime("%Y")
    posts = explode_tags(posts)

    # Clean up tag names
    selected_tags = get_selected_tags(config)
    posts = posts.merge(selected_tags, "left", left_on="tag", right_index=True)
    posts.drop("tag", axis=1, inplace=True)
    posts.rename(columns={"newname": "tag"}, inplace=True)
    posts.loc[:, "tag"] = posts["tag"].where(pd.notnull(posts["tag"]), "Other")

    #
    # Create final data sets
    #

    os.chdir("data")

    # List of tags
    selected_tags["newname"].to_json("tags.json", orient="values")

    # list of countries
    country_table(users).to_json("countries.json", orient="index")

    # Count and relative frequency of tags by year (line chart)
    summary_table(posts, group_by=["tag", "year"], freq=True,
                  freq_by="year").to_csv("tag_year.csv")

    # Count and relative frequency of tags by country (bar chart / choropleth)
    country_tag = summary_table(posts, group_by=["country", "tag"],
                                freq=True, freq_by="country")

    # Worldwide count and relative frequency of tags (bar char)
    worldwide_tag = summary_table(posts, group_by=["tag"], freq=True)
    worldwide_tag["country"] = "XXX"
    worldwide_tag.set_index("country", append=True, inplace=True)
    worldwide_tag = worldwide_tag.reorder_levels(["country", "tag"])

    country_tag.append(worldwide_tag).to_csv("country_tag.csv")

    # Tag co-occurrence matrix (chord diagram)
    tag_matrix(posts).to_json("tag_matrix.json")


def summary_table(posts, group_by, freq=False, freq_by=None):
    df = posts.reset_index().groupby(group_by).count()[["index"]]
    df.rename(columns={"index": "count"}, inplace=True)

    if freq:
        if freq_by is None:
            by = df
        else:
            by = df.groupby(level=freq_by)
        df["freq"] = df / by.sum()

    return df


def country_table(users):
    countries = users.reset_index()
    countries = countries.groupby("country").count()

    countries.rename(columns={"user": "users"}, inplace=True)

    countries["name"] = countries.index.map(lambda country:
        pycountry.countries.get(alpha_3=country).name)

    return countries


def tag_matrix(posts):
    posts = posts[["tag", "user"]].reset_index()
    user_tag = posts.groupby(["tag", "user"]).count()
    user_tag = user_tag.reset_index().set_index("user")[["tag"]]

    tag_pairs = user_tag.join(user_tag, lsuffix="1", rsuffix="2")
    tag_pairs = tag_pairs.reset_index().groupby(["tag1", "tag2"]).count()
    tag_pairs = tag_pairs.rename(columns={"user": "count"}).reset_index()

    return tag_pairs.pivot("tag1", "tag2", "count")


def merge_users_countries(users, locations):
    users = users.reset_index()
    users = users.merge(locations, "left", on="Location")[["Id", "Country"]]

    users.rename(columns={"Id": "user", "Country": "country"}, inplace=True)
    users.set_index("user", inplace=True)

    return users[pd.notnull(users["country"])]


def merge_posts_countries(posts, users):
    posts = posts.merge(users, "left", left_on="OwnerUserId",
                        right_index=True)

    # Use None instead of NaN for missing countries
    posts.loc[:, "country"] = posts["country"].where(
                                  pd.notnull(posts["country"]), None)

    return posts


def explode_tags(posts):
    posts = posts.copy()

    # Tags are stored as a string in the format "<tag1><tag2><tag3>".
    # We want to convert this string to a list of strings, where each
    # element of the list is a tag. First, we remove the first ("<")
    # and last (">") characters of the string, and then we split it on
    # the delimiters in the middle ("><").
    posts["Tags"] = posts["Tags"].str[1:-1].str.split("><")

    # In the data dump, only questions have tags. Since we also want
    # to consider answers, we set the tags of the answers to the same
    # value as their parent question.
    answers_tags = posts[posts.PostTypeId == 2][["ParentId"]]
    answers_tags = answers_tags.join(posts[["Tags"]], on="ParentId")
    posts.update(answers_tags[["Tags"]])

    # Keep only the columns we are going to use
    posts = posts[["year", "Tags", "OwnerUserId", "country"]]
    posts.rename(columns={"OwnerUserId": "user"}, inplace=True)

    # Keep only posts that have at least one tag
    posts = posts[~pd.isnull(posts["Tags"])]

    # Finally, explode the posts table, so that each post appears
    # n times, where n is the number of tags on that post. Each
    # observation of a post will have a single tag.
    new_index = np.hstack([[post_id] * len(tag) for post_id, tag
                           in posts["Tags"].iteritems()])
    posts_tags = pd.DataFrame({"tag": np.hstack(posts["Tags"])}, new_index)

    return posts_tags.join(posts[["year", "user", "country"]])


def get_selected_tags(config):
    df = pd.read_csv(config["Filters"]["selected_tags"])
    df = df[df["selected"] == 1]

    # Sort by correctly-formatted name
    df.set_index("newname", drop=False, inplace=True)
    df = df.reindex(sorted(df.index, key=lambda x: x.lower()))

    return df.set_index("tag")[["newname"]]


if __name__ == "__main__":
    main()
