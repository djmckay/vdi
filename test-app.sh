#bin/sh

send_and_log() {
    local method=$1
    local endpoint=$2
    local token=$3
    local data=$4
    local log_file="curl_logs.txt"

    # Create a temporary file for verbose output
    local temp_file=$(mktemp)

    # Construct and execute curl command with verbose logging
    response=$(curl --location \
        --request "${method}" \
        --header "X-Hub-Signature: ${token}" \
        --header "X-Atlassian-Webhook-Identifier: ${token}" \
        --header 'Content-Type: application/json' \
        --verbose \
        --stderr "${temp_file}" \
        "${testUrl}${endpoint}" \
        ${data:+ --data-raw "$data"})
#        --write-out "\nStatus Code: %{http_code}\nTotal Time: %{time_total}s\n" \

    # Get the timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    # Log the request and response
    {
        echo "=== ${timestamp} ==="
        echo "REQUEST:"
        echo "Method: ${method}"
        echo "Endpoint: ${endpoint}"
        echo "Token: ${token}"
        echo "Data: ${data}"
        echo -e "\nRESPONSE:"
        cat "${temp_file}"
        echo "Response Body:"
        echo "${response}" | jq '.' 2>/dev/null || echo "${response}"
        echo "======================================="
        echo
    } >> "${log_file}"

    # Clean up temp file
    rm "${temp_file}"

    # Return the response
    echo "${response}"
}

echo $(cat target/output.json | jq -r '.DisneyStack.ApiEndpoint')
  testUrl=$(cat target/output.json | jq -r '.DisneyStack.ApiEndpoint')
#
echo "Post"
ID_TOKEN_AC="sha256=9335e64405a27cd66d06e5f25da7b10ec8cd507f7dfacb5a0d0105d2d0ee2594"

response=$(send_and_log "POST" "" "$ID_TOKEN_AC" '{
    "issue": {
        "id":"99292",
        "self":"https://your-domain.atlassian.net/rest/api/2/issue/99291",
        "key":"JRA-20002",
        "fields":{
            "status":"approved",
            "summary":"I feel the need for speed",
            "created":"2009-12-16T23:46:10.612-0600",
            "description":"Make the issue nav load 10x faster",
            "labels":["UI", "dialogue", "move"],
            "priority": {
                "self": "https://your-domain.atlassian.net/rest/api/2/priority/3",
                "iconUrl": "https://your-domain.atlassian.net/images/icons/priorities/minor.svg",
                "name": "Minor",
                "id": "3"
            }
        }
    },
    "user": {
        "self":"https://your-domain.atlassian.net/rest/api/2/user?accountId=99:27935d01-92a7-4687-8272-a9b8d3b2ae2e",
        "accoundId": "99:27935d01-92a7-4687-8272-a9b8d3b2ae2e",
        "accountType": "atlassian",
        "avatarUrls":{
            "16x16":"https://your-domain.atlassian.net/secure/useravatar?size=small&avatarId=10605",
            "48x48":"https://your-domain.atlassian.net/secure/useravatar?avatarId=10605"
        },
        "displayName":"Bryan Rollins [Atlassian]",
        "active" : "true",
        "timeZone": "Europe/Warsaw"
    },
    "changelog": {
        "items": [
            {
                "toString": "A new summary.",
                "to": null,
                "fromString": "What is going on here?????",
                "from": null,
                "fieldtype": "jira",
                "field": "summary"
            },
            {
                "toString": "New Feature",
                "to": "2",
                "fromString": "Improvement",
                "from": "4",
                "fieldtype": "jira",
                "field": "issuetype"
            }
        ],
        "id": 10124
    },
    "timestamp": 1606480436302,
    "webhookEvent": "jira:issue_updated",
    "issue_event_type_name": "issue_generic"
}
')

 echo $response
 echo $response | jq -r ".id"