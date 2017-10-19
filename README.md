# atlasdigital_freshdesk
Tools to work with Freshdesk (freshdesk.com)

There isn't an easy way to update many ticket's company within the freshdesk.com UI. 
This tool is intended automate that process.

Currently, we quickly update Tickets by changing a Ticket's Requester ID from a temporary Requestor ID to the intended Requester ID.

This tool is currently early alpha with updates to come.

Create a config.json file with
{
    "freshdesk":{
        "domain":"your-freshdesk-domain",
        "user":"your-user",
        "pswd":"your-user-password",
        "temp_requester_id":temp-requester-id
    }
}
