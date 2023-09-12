# Copyright (C) 2023 TraceTronic GmbH
#
# SPDX-License-Identifier: MIT

commit_sha=$1
token=$2

sudo apt-get update
sudo apt-get install -y jq curl

commit_info=$(curl --fail -k -L \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $token" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/tracetronic/ecu-test_custom-checks/commits/$commit_sha/pulls)

chore_label_list=$(echo "$commit_info" | jq -r '.[]')

if [ -z "$chore_label_list" ]; then
  echo "ERROR: No pull request found for commit. Was this pipeline triggered other than via a merge to main?"
  exit 42
fi

chore_label=$(echo "$commit_info" | jq -r '.[0].labels[]|select(.name=="chore")')

if [ -n "$chore_label" ]; then
  echo "withoutChoreLabel=false" >> "$GITHUB_ENV"
else
  echo "withoutChoreLabel=true" >> "$GITHUB_ENV"
fi
