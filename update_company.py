import requests
import json

def getapiURL (domain):
    api_url = "https://" + str(domain) + ".freshdesk.com/api/v2/"
    return api_url

def getTicketURL (api_url,ticket_id):
    ticket_url = str(api_url) + "tickets/" + str(ticket_id)
    return ticket_url

def getTicketsURLEmailCompany (api_url,customer_email,company):
    tickets_url = str(api_url) + "tickets?email=" + str(customer_email) + "&company_id=" + str(company)
    return tickets_url

def getTickets (user_email,pswd,tickets_url,headers):
    tickets_found = list()
    #curl -u eric@***REMOVED***:***REMOVED*** -H "Content-Type: application/json" -X GET 'https://atlasdigitalsupport.freshdesk.com/api/v2/tickets?email=cdixon@***REMOVED***&company_id=5000236189'
    r = requests.get(tickets_url, auth=(user_email,pswd), headers=headers)
    #print(r.json())
    for tickets in r.json():
        for attribute, value in tickets.iteritems():
            # I think there's better way
            if attribute == "id":
                tickets_found.append(value)
    return tickets_found

def updateCompany (user_email,pswd,ticket_id,temp_requester_id,requester_id,ticket_url,headers):
    #curl -u eric@***REMOVED***:***REMOVED*** -H "Content-Type: application/json" -X PUT -d '{"requester_id":12003568550}' 'https://atlasdigitalsupport.freshdesk.com/api/v2/tickets/10176'
    # TODO: type of ticket
    # TODO: type of group: PilotWare Support = 12000000933, Technical Support = 5000175231, Sales = 5000188665
    update_info = {'requester_id':temp_requester_id,'type':'Technical Support', 'group_id':5000175231}
    r = requests.put(ticket_url, auth=(user_email,pswd), headers=headers, data = json.dumps(update_info))
    print user_email,pswd,ticket_id,temp_requester_id,requester_id,ticket_url,headers
    print  r.text
    #curl -u eric@***REMOVED***:***REMOVED*** -H "Content-Type: application/json" -X PUT -d '{"requester_id":5007580195}' 'https://atlasdigitalsupport.freshdesk.com/api/v2/tickets/10176'
    #r = requests.put(ticket_url, auth=(user_email,pswd), headers=headers, data={"requester_id":"requester_id"})

def main():
    json_headers = {'Content-type': 'application/json'}
    # statics by variable or config
    domain = "atlasdigitalsupport"
    user = "eric@***REMOVED***"
    pswd = "***REMOVED***"
    temp_requester_id = 12003568550
    # to be provided
    requester_email = "cdixon@***REMOVED***"
    old_company_id = 5000236189
    new_company_id = ""
    # to be derived by email
    requester_id = 5007580195
    api_url = getapiURL(domain)
    tickets_url = getTicketsURLEmailCompany(api_url,requester_email,old_company_id)
    print(tickets_url)

    # TODO: change this list to a hash
    # TODO: which fields are "required_for_agents": true
    # TODO: type of ticket  'Technical Support,Site Survey,Phone Support,Installation,Sales'
    # TODO: type of group: PilotWare Support = 12000000933, Technical Support = 5000175231, Sales = 5000188665
    ticket_ids = getTickets(user,pswd,tickets_url,json_headers)

    # TODO: iterate hash
    for ticket_id in ticket_ids:
        ticket_url = getTicketURL(api_url,ticket_id)
        #updateCompany(user,pswd,ticket_id,temp_requester_id,requester_id, ticket_url, json_headers)
        #exit()
        print ticket_id 
if __name__ == "__main__":
    main()
