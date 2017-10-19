"""This module is needed for handling json"""
import json

# third-party module
import requests
from email_validator import validate_email, EmailNotValidError

def get_api_url(domain):
    """Return the freshdesk API URL."""
    api_url = "https://" + str(domain) + ".freshdesk.com/api/v2/"
    return api_url

def get_ticket_url_by_id(api_url, ticket_id):
    """Return the API URL for provided ticket id"""
    ticket_url = str(api_url) + "tickets/" + str(ticket_id)
    return ticket_url

def get_tickets_url_by_email_cmpny(api_url, customer_email, company):
    """Return the API URL for provided ticket email and company"""
    tickets_url = str(api_url) + "tickets?email=" + str(customer_email) \
    + "&company_id=" + str(company)
    return tickets_url

def get_contact_url_by_email(api_url, customer_email):
    """Return the API URL for provided email"""
    contacts_url = str(api_url) + "contacts?email=" + str(customer_email)
    return contacts_url

def get_user_id_by_email(user_email, pswd, contacts_url, headers):
    """Return user ID for provided email"""
    rjson = requests.get(contacts_url, auth=(user_email, pswd), headers=headers)
    for fields in rjson.json():
        if fields['id']:
            return fields['id']

def get_tickets(user_email, pswd, tickets_url, headers):
    """Return tickets found for email and company provided"""
    tickets_found = {}
    #curl -u eric@atlasdigital.tv:pass -H "Content-Type: application/json" -X GET \
    # 'https://atlasdigitalsupport.freshdesk.com/api/v2/tickets?\
    # email=cdixon@atlasdigital.tv&company_id=5000236189'
    rjson = requests.get(tickets_url, auth=(user_email, pswd), headers=headers)
    for tickets in rjson.json():
        ticket_found = {}
        ticket_found['group_id'] = tickets['group_id']
        ticket_found['type'] = tickets['type']
        ticket_found['description_text'] = tickets['description_text']
        tickets_found[tickets['id']] = ticket_found
    return tickets_found

def get_ticket_types_by_label(api_url, user_email, pswd, headers, label):
    """Return field choices for provided label"""
    rjson = requests.get(api_url+"ticket_fields", auth=(user_email, pswd), headers=headers)
    for fields in rjson.json():
        if fields['label'] == label:
            return fields['choices']

def ask_for_ticket_type_num(ticket_id, ticket_desc_text, ticket_types):
    """Return ticket type number for ticket field choices"""
    print "\nTicket " + str(ticket_id), \
        " does not have a Type set, type the number of which", \
        "Type you want (Type 0 for Ticket description)"
    num = 1
    for ticket_type in ticket_types:
        print "  ("+str(num)+"): " + ticket_type
        num += 1
    ticket_type_num = input("Type: ")
    if ticket_type_num == 0:
        print "\n" + ticket_desc_text
        ticket_type_num = ask_for_ticket_type_num(ticket_id, ticket_desc_text, ticket_types)
    return ticket_type_num

def update_company(
        user_email, pswd, temp_requester_id, requester_id, ticket_url, ticket_type, headers):
    """Update company with temp requester ID, then update with real requestor ID"""
    #curl -u eric@atlasdigital.tv:pass -H "Content-Type: application/json" -X PUT -d \
    #'{"requester_id":12003568550}' 'https://atlasdigitalsupport.freshdesk.com/api/v2/tickets/10176'
    temp_update_info = {
        'requester_id':temp_requester_id, 'type':ticket_type}
    requests.put(
        ticket_url, auth=(user_email, pswd), headers=headers, data=json.dumps(temp_update_info))

    #curl -u eric@atlasdigital.tv:pass -H "Content-Type: application/json" -X PUT -d \
    # '{"requester_id":5007580195}' 'https://atlasdigitalsupport.freshdesk.com/api/v2/tickets/10176'
    final_update_info = {
        'requester_id':requester_id}
    requests.put(
        ticket_url, auth=(user_email, pswd), headers=headers, data=json.dumps(final_update_info))

def main():
    """Main function to ask User for information to update Ticket Company"""
    json_headers = {'Content-type': 'application/json'}
    # config
    with open('config.json') as json_data_file:
        configjsondata = json.load(json_data_file)
    domain = configjsondata['freshdesk']['domain']
    user = configjsondata['freshdesk']['user']
    pswd = configjsondata['freshdesk']['pswd']
    temp_requester_id = configjsondata['freshdesk']['temp_requester_id']
    # to be provided
    requester_email = raw_input("Requester email: ") # cdixon@atlasdigital.tv
    try:
        valid_email = validate_email(requester_email) # validate and get info
        requester_email = valid_email["email"] # replace with normalized form
    except EmailNotValidError as email_error:
        # email is not valid, exception message is human-readable
        print str(email_error)
        exit()

    old_company_id = raw_input("Old Company ID: ") #5000236189 - atlasdigital
    # todo future: options for changing one company to another without a person
    #new_company_id = ""

    api_url = get_api_url(domain)

    contacts_url = get_contact_url_by_email(api_url, requester_email)
    # requester_id - derived by email
    requester_id = get_user_id_by_email(user, pswd, contacts_url, json_headers) #5007580195

    tickets_url = get_tickets_url_by_email_cmpny(api_url, requester_email, old_company_id)

    #todo: which fields are "required_for_agents": true
    ticket_ids = get_tickets(user, pswd, tickets_url, json_headers)

    for ticket_id in ticket_ids.iteritems():
        ticket_url = get_ticket_url_by_id(api_url, ticket_id[0])
        # If there's no Type set, get available types and ask user selection
        # Type of ticket  'Technical Support,Site Survey,Phone Support,Installation,Sales'
        if ticket_id[1]['type'] == "No Type Set":
            ticket_types = get_ticket_types_by_label(api_url, user, pswd, json_headers, "Type")
            ticket_type_num = ask_for_ticket_type_num(
                ticket_id[0], ticket_id[1]['description_text'], ticket_types)
            ticket_type = ticket_types[ticket_type_num-1]
            print ticket_type
        else:
            ticket_type = ticket_id[1]['type']

        '''possible future todo: type of group:
        PilotWare Support = 12000000933, 
        Technical Support = 5000175231, 
        Sales = 5000188665
        '''
        update_company(
            user, pswd, temp_requester_id, requester_id, ticket_url, ticket_type, json_headers)

if __name__ == "__main__":
    main()
