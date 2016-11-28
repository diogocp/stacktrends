#!/usr/bin/env python3

import configparser
import sqlite3

import numpy as np
import pandas as pd


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

    # Merges
    users_countries = merge_users_countries(users, locations)
    posts_countries = merge_posts_countries(posts, users_countries)
    posts_exploded = explode_tags(posts_countries)

    # Apply filters (configure in stacktrends.ini)
    my_countries = filter_countries(users_countries, posts_countries, config)
    my_tags = filter_tags(config)

    my_posts = posts_exploded[posts_exploded["Country"].isin(my_countries)]
    my_posts = my_posts[my_posts["Tag"].isin(my_tags)]

    # Simplify column names
    my_posts = my_posts.rename(columns={"Tag": "tag",
                                        "CreationDate": "date",
                                        "OwnerUserId": "user",
                                        "Country": "country"})

    # Output to SQLite database
    con = sqlite3.connect(config["Database"]["filename"])
    my_posts.to_sql("my_posts", con, if_exists="replace", index_label="post")
    con.close()

    # Create summary datasets
    summary_table(my_posts).to_csv("tag.csv")
    summary_table(my_posts, period="month").to_csv("tag_month.csv")
    summary_table(my_posts, period="year").to_csv("tag_year.csv")
    summary_table(my_posts, by_country=True).to_csv("country_tag.csv")
    summary_table(my_posts, "month", True).to_csv("country_tag_month.csv")
    summary_table(my_posts, "year", True).to_csv("country_tag_year.csv")

    tag_correlation_table(my_posts).to_csv("tag_correlation.csv")


def summary_table(posts, period=None, by_country=False):
    posts = posts[["country", "tag", "date"]].reset_index()

    groups = ["tag"]
    if by_country:
        groups = ["country"] + groups
    if period is not None:
        groups = groups + ["date"]

        if period == "year":
            posts["date"] = posts["date"].dt.strftime("%Y")
        elif period == "quarter":
            raise NotImplemented
        elif period == "month":
            posts["date"] = posts["date"].dt.strftime("%Y-%m")
        else:
            raise ValueError("Invalid period '%s'" % period)

    return posts.groupby(groups).count()["index"].rename()


def tag_correlation_table(posts):
    posts = posts[["tag", "user"]].reset_index()
    user_tag = posts.groupby(["tag", "user"]).count()
    user_tag = user_tag.reset_index().set_index("user")[["tag"]]

    tag_pairs = user_tag.join(user_tag, lsuffix="1", rsuffix="2")
    tag_pairs = tag_pairs.reset_index().groupby(["tag1", "tag2"]).count()
    tag_pairs = tag_pairs.rename(columns={"user": "both"}).reset_index()

    totals = user_tag.reset_index().groupby("tag").count()
    tag_pairs = tag_pairs.merge(totals, left_on="tag1", right_index=True)
    tag_pairs = tag_pairs.rename(columns={"user": "first"})

    tag_pairs["prob"] = tag_pairs["both"] / tag_pairs["first"]

    return tag_pairs.set_index(["tag1", "tag2"])["prob"]


def merge_users_countries(users, locations):
    users = users.reset_index()
    users = users.merge(locations, "left", on="Location")[["Id", "Country"]]
    users.set_index("Id", inplace=True)

    return users[pd.notnull(users["Country"])]


def merge_posts_countries(posts, users):
    posts = posts.merge(users, "left", left_on="OwnerUserId",
                        right_index=True)

    # Use None instead of NaN for missing countries
    posts.loc[:, "Country"] = posts["Country"].where(
                                  pd.notnull(posts["Country"]), None)

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
    posts = posts[["CreationDate", "Tags", "OwnerUserId", "Country"]]

    # Keep only posts that have at least one tag
    posts = posts[~pd.isnull(posts["Tags"])]

    # Finally, explode the posts table, so that each post appears
    # n times, where n is the number of tags on that post. Each
    # observation of a post will have a single tag.
    new_index = np.hstack([[post_id] * len(tag) for post_id, tag
                           in posts["Tags"].iteritems()])
    posts_tags = pd.DataFrame({"Tag": np.hstack(posts["Tags"])}, new_index)

    return posts_tags.join(posts[["CreationDate", "OwnerUserId", "Country"]])


def filter_countries(users_countries, posts_countries, config):
    min_users = int(config["Filters"]["min_users_per_country"])
    min_posts = int(config["Filters"]["min_posts_per_country"])

    num_users = users_countries.reset_index().groupby("Country")["Id"].count()
    ok_users = num_users[num_users >= min_users].index

    num_posts = posts_countries.reset_index().groupby("Country")["Id"].count()
    ok_posts = num_posts[num_posts >= min_posts].index

    return ok_users.intersection(ok_posts)


def filter_tags(config):
    selected_tags = pd.read_csv(config["Filters"]["selected_tags"])
    selected_tags = selected_tags[selected_tags["selected"] == 1]

    return selected_tags.set_index("tag").index


if __name__ == "__main__":
    main()
