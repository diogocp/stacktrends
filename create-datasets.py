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
    posts = posts[["CreationDate", "Tags", "OwnerUserId"]]

    # Keep only posts that have at least one tag
    posts = posts[~pd.isnull(posts["Tags"])]

    # Explode the posts table, so that each post appears n times,
    # where n is the number of tags on that post. Each observation
    # of a post will have a single tag.
    new_index = np.hstack([[post_id] * len(tag) for post_id, tag
                           in posts["Tags"].iteritems()])
    posts_tags = pd.DataFrame({"Tag": np.hstack(posts["Tags"])}, new_index)
    posts_long = posts_tags.join(posts[["CreationDate", "OwnerUserId"]])


if __name__ == "__main__":
    main()
