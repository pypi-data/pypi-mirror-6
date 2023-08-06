#!/usr/bin/env python
"""
Copyright 2013 Reed O'Brien <reed@reedobrien.com>.
All rights reserved. Use of this source code is governed by a
BSD-style license that can be found in the LICENSE file.


Purpose: Create groups, users, and roles from yaml config
"""
from __future__ import unicode_literals

import logging
import os
import sys

import botocore.session

from btx import BTX

from botool.common import (
    parse_args,
    setup_arg_parser
)


def main():
    parser = setup_arg_parser()
    parser.add_argument("-o", "--output_dir", type=str,
                        help="put creds for users here. "
                        "Default: current directory")
    parser.add_argument("-p", "--policy_dir", type=str, default="policies",
                        help="where policy documents (JSON) are located. "
                        "Default: ./policies")
    parser.add_argument("-a", "--all", action="store_true",
                        help="Process users, groups, and roles")
    parser.add_argument("-r", "--roles", action="store_true",
                        help="process roles")
    parser.add_argument("-g", "--groups", action="store_true",
                        help="process groups")
    parser.add_argument("-u", "--users", action="store_true",
                        help="process users")
    args = parse_args(parser)
    if not args.all or args.roles or args.groups or args.users:
        parser.error("No targets specified, "
                     "must be one of -a, -r, -g, -u")
    botox = BTX(args.config, debug=args.verbose, dryrun=args.dryrun,
                region=args.region)

    if args.all:
        args.roles = args.groups = args.users = True

    if args.roles:
        if botox.config["roles"]:
            assert os.path.isdir(args.policy_dir)
            for role in botox.config["roles"]:
                botox("CreateRole", role_name=role["role_name"],
                      assume_role_policy_document=botox.policy_string(
                          os.path.join(args.policy_dir,
                                       role["assume_role_policy_document"])))
                botox("PutRolePolicy", role_name=role["role_name"],
                      policy_name=role["policy_name"],
                      policy_document=botox.policy_string(
                          os.path.join(args.policy_dir, role["policy_document"]
                                       )))
        if botox.config["profiles"]:
            for profile in botox.config["profiles"]:
                botox("CreateInstanceProfile",
                      instance_profile_name=profile["instance_profile_name"])
                botox("AddRoleToInstanceProfile", **profile)

    if args.groups:
        if botox.config["groups"]:
            for group in botox.config["groups"]:
                botox("CreateGroup", group_name=group["group_name"])
                group["policy_document"] = botox.policy_string(os.path.join(
                    args.policy_dir, group["policy_document"]))
                botox("PutGroupPolicy", **group)

    if args.users:
        if botox.config["users"]:
            for user in botox.config["users"]:
                user_name = user["user_name"]
                groups = user["groups"]
                r, d = botox("GetUser", user_name=user_name)
                if r.status_code == 404:
                    r, d = botox("CreateUser", user_name=user_name)
                    if r.ok:
                        ## Only creates when we create a user
                        ## add flag for creating key? prolly not since that is
                        ## a one of and appropriate for the console.
                        r, d = botox("CreateAccessKey", user_name=user_name)
                        if r.ok:
                            keys = sorted(d["AccessKey"].keys())
                            if args.output_dir:
                                if os.path.exists(args.output_dir):
                                    assert os.path.isdir(args.output_dir)
                                else:
                                    os.makedirs(args.output_dir)
                                path = os.path.join(args.output_dir,
                                                    "{}.csv".format(user_name))
                            else:
                                path = "{}.csv".format(user_name)
                            with open(path, "w") as f:
                                f.write(",".join(keys))
                                f.write("\n")
                                f.write(",".join([d["AccessKey"][k] for k
                                        in keys]))
                                f.write("\n")
                r, d = botox("ListGroupsForUser", user_name=user_name)
                if r.ok:
                    existing = d.get("Groups", [])
                if groups:
                    for group in groups:
                        if group not in existing:
                            botox("AddUserToGroup",
                                  user_name=user_name,
                                  group_name=group)
                for membership in existing:
                    if membership["GroupName"] not in groups:
                        botox("RemoveUserFromGroup",
                              user_name=user_name,
                              group_name=membership["GroupName"])

if __name__ == "__main__":
    main()
