from MyInfo.models import UserDataItem

# Turn a queryset into an appropriate initial-values dictionary for the contact information form.
def contact_initial(request):
    psu_uuid = request.session['identity']['PSU_UUID']
    (email, _) = UserDataItem.objects.get_or_create(psu_uuid=psu_uuid, key_name='EXTERNAL_EMAIL_ADDRESS', defaults={'key_valu' : ''})
    (cell, _) = UserDataItem.objects.get_or_create(psu_uuid=psu_uuid, key_name='CELL_PHONE_NUMBER', defaults={'key_valu' : ''})
    (carr, _) = UserDataItem.objects.get_or_create(psu_uuid=psu_uuid, key_name='CELL_PHONE_CARRIER', defaults={'key_valu' : ''})
    
    data = {
        'alternate_email' : email.key_valu,
        'cell_number' : cell.key_valu,
        'cell_carrier' : carr.key_valu
    }
    
    if email.key_valu != '' or (cell.key_valu != '' and carr.key_valu is not None):
        request.session['supernag'] = False
    else:
        request.session['supernag'] = True
    
    return data

# Turn a queryset into an appropriate initial-values dictionary for the directory information form.
def directory_initial(psu_uuid):
    title = UserDataItem.objects.get_or_create(psu_uuid=psu_uuid, key_name='PSU_EMPLOYEE_TITLE', defaults={'key_valu' : ''})
    department = UserDataItem.objects.get_or_create(psu_uuid=psu_uuid, key_name='PSU_EMPLOYEE_DEPARTMENT_NAME', defaults={'key_valu' : ''})
    office = UserDataItem.objects.get_or_create(psu_uuid=psu_uuid, key_name='PSU_EMPLOYEE_OFFICE_INFO', defaults={'key_valu' : ''})
    
    data = {}
    
    data['job_title'] = title[0].key_valu
    data['department'] = department[0].key_valu
    data['office_location'] = office[0].key_valu
    
    return data

# Return a form error state into html code.
def error_state_to_html(form):
    error_state = '<ul>'
    
    for field in form.errors:
        for value in form.errors[field]:
            if field == '__all__': # General form validation error, so there won't be a field label.
                error_state = error_state + '<li>' + value + '</li>'
            else:
                error_state = error_state + '<li>' + form[field].label + ': ' + value + '</li>'
            
    error_state = error_state + '</ul>'
    return error_state
