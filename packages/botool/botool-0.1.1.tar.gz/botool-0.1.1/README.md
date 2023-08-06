botool
======

Hopefully useful botocore scripts for managing aws resources

TODO
----

IAM
---

 - add backup flag to write out settings to file(s)
 - add capacity to remove users, groups, and roles
 - tests
 - allow "users" to have individual policies


Example Config
--------------

    service: IAM

    groups:
      - group_name: "group1"
        policy_name: "allow-rw-to-s3"
        policy_document: "example-allow-rw-to-s3.json"
      - group_name: "group2"
        policy_name: "allow-rw-to-s3"
        policy_document: "example-allow-rw-to-s3.json"
      - group_name: "group3"
        policy_name: "allow-rw-to-s3"
        policy_document: "example-allow-rw-to-s3.json"

    users:
      - user_name: "user1"
        groups: [group2, group1]
      - user_name: "user2"
        groups: [group1]
      - user_name: "user3"
        groups: [group3, group2, group1]
      - user_name: "user4"
        groups: [group2, group3]

    roles:
      - role_name: "role1-service"
        policy_name: "allow-rw-to-s3"
        assume_role_policy_document: "allow-assume-role-by-ec2-service.json"
        policy_document: "example-allow-rw-to-s3.json"
      - role_name: "role2-service"
        policy_name: "allow-rw-to-s3"
        assume_role_policy_document: "allow-assume-role-by-ec2-service.json"
        policy_document: "example-allow-rw-to-s3.json"
      - role_name: "role3-service"
        policy_name: "allow-rw-to-s3"
        assume_role_policy_document: "allow-assume-role-by-ec2-service.json"
        policy_document: "example-allow-rw-to-s3.json"


Example Policies
----------------

allow-assume-role-by-ec2-service.json
-------------------------------------

    {
        "Statement":
        [
            {
                "Effect": "Allow",
                "Action": [
                    "sts:AssumeRole"
                    ],
                "Principal":
                {
                    "Service" :
                    [
                        "ec2.amazonaws.com"
                    ]
                }
            }
        ]
    }

example-allow-rw-to-s3.json
---------------------------

    {
        "Version":"2012-10-17",
        "Statement":
            [
                {
                    "Effect":"Allow",
                    "Action":
                    [
                    "s3:AbortMultipartUpload",
                    "s3:DeleteObject",
                    "s3:GetObject",
                    "s3:GetObjectAcl",
                    "s3:ListMultipartUploadParts",
                    "s3:PutObject",
                    "s3:PutObjectAcl"
                    ],
                    "Resource":
                        [
                        "arn:aws:s3:::hqmigrat-stage/*"
                        ]
                },
                {
                    "Sid":"Stmt1391189122000",
                    "Effect":"Allow",
                    "Action":
                    [
                    "s3:AbortMultipartUpload",
                    "s3:DeleteObject",
                    "s3:GetObject",
                    "s3:GetObjectAcl",
                    "s3:ListMultipartUploadParts",
                    "s3:PutObject",
                    "s3:PutObjectAcl"
                    ],
                    "Resource":
                    [
                    "arn:aws:s3:::hqmigrat-prod/*"
                    ]
                }
            ]
    }
