from MyInfo.forms import formExternalContactInformation, formPSUEmployee
from MyInfo.util_functions import error_state_to_html
from models import UserDataItem

def update_password(request):
    pass
    # TODO: Move the password update here. I guess we live in an ajax world now.

def update_external_contact(request):
    form = formExternalContactInformation(request.POST or None)
    
    if form.is_valid():
        UserDataItem.objects.filter(psu_uuid = request.session['identity']['PSU_UUID']).filter(key_name = 'EXTERNAL_EMAIL_ADDRESS'). \
        update(key_valu = form.cleaned_data['alternate_email'])
        
        UserDataItem.objects.filter(psu_uuid = request.session['identity']['PSU_UUID']).filter(key_name = 'CELL_PHONE_NUMBER'). \
        update(key_valu = form.cleaned_data['cell_number'])
        
        UserDataItem.objects.filter(psu_uuid = request.session['identity']['PSU_UUID']).filter(key_name = 'CELL_PHONE_CARRIER'). \
        update(key_valu = form.cleaned_data['cell_carrier'])
        
        if form.cleaned_data['alternate_email'] != '' or (form.cleaned_data['cell_number'] != '' and form.cleaned_data['cell_carrier'] is not None):
            request.session['supernag'] = False
        else:
            request.session['supernag'] = True
        
        return {'status' : 'Success', 'message' : '<p>Contact information updated successfully.</p>'}
    
    return {'status' : 'Error', 'message' : error_state_to_html(form)}

def update_directory_information(request):
    form = formPSUEmployee(request.POST or None)
    
    if request.session['supernag'] is True and request.session['opt-out'] is False:
        return {'status' : 'Error', 'message' : "<p>You must provide password reset information to continue.</p>"}
    
    if form.is_valid():
        UserDataItem.objects.filter(psu_uuid = request.session['identity']['PSU_UUID']).filter(key_name = 'PSU_EMPLOYEE_TITLE'). \
        update(key_valu = form.cleaned_data['job_title'])
        
        UserDataItem.objects.filter(psu_uuid = request.session['identity']['PSU_UUID']).filter(key_name = 'PSU_EMPLOYEE_DEPARTMENT_NAME'). \
        update(key_valu = form.cleaned_data['department'])
        
        UserDataItem.objects.filter(psu_uuid = request.session['identity']['PSU_UUID']).filter(key_name = 'PSU_EMPLOYEE_OFFICE_INFO'). \
        update(key_valu = form.cleaned_data['office_location'])
        
        return {'status' : 'Success', 'message' : '<p>Directory information updated successfully.</p>'}
    
    return {'status' : 'Error', 'message' : error_state_to_html(form)}

def toggle_password_opt_out(request):
    request.session["opt-out"] = not request.session["opt-out"]