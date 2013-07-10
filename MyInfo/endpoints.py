from MyInfo.forms import formExternalContactInformation, formPSUEmployee
from MyInfo.forms import formPasswordChange, formNewPassword
from MyInfo.util_functions import error_state_to_html
from PSU_MyInfo.api_calls import change_password
from django.core.exceptions import SuspiciousOperation
from models import UserDataItem
from ajax.decorators import login_required

import logging
logger = logging.getLogger(__name__)

@login_required
def update_password(request):
    # Find out which auth backend we used, is this a new user or returning user?
    # TODO: Do we want to send the new user somewhere, or send them an email?
    new_user = False;
    if request.session['_auth_user_backend'] == 'django_cas.backends.CASBackend':
        form = formPasswordChange(request.POST or None)
    else:
        form = formNewPassword(request.POST or None)
        new_user = True;

    if form.is_valid():
        (success, message) = change_password(request.session['identity'], form.cleaned_data['newPassword'])
        if success:
            return {'status' : 'Success', 'message' : '<p>Password changed successfully.</p>'}
        else:
            return {'status' : 'Error', 'message' : '<p>{}</p>'.format(message)}
    else:
        return {'status' : 'Error', 'message' : error_state_to_html(form)}
        

@login_required
def update_external_contact(request):
    form = formExternalContactInformation(request.POST or None)
    ident = request.session['identity']['PSU_UUID']
    
    if form.is_valid():
        UserDataItem.objects.filter(psu_uuid = ident).filter(key_name = 'EXTERNAL_EMAIL_ADDRESS'). \
        update(key_valu = form.cleaned_data['alternate_email'])
        
        UserDataItem.objects.filter(psu_uuid = ident).filter(key_name = 'CELL_PHONE_NUMBER'). \
        update(key_valu = form.cleaned_data['cell_number'])
        
        UserDataItem.objects.filter(psu_uuid = ident).filter(key_name = 'CELL_PHONE_CARRIER'). \
        update(key_valu = form.cleaned_data['cell_carrier'])
        
        if form.cleaned_data['alternate_email'] != '' or (form.cleaned_data['cell_number'] != '' and form.cleaned_data['cell_carrier'] is not None):
            request.session['supernag'] = False
        else:
            request.session['supernag'] = True
        
        return {'status' : 'Success', 'message' : '<p>Contact information updated successfully.</p>'}
    
    return {'status' : 'Error', 'message' : error_state_to_html(form)}

@login_required
def update_directory_information(request):
    form = formPSUEmployee(request.POST or None)
    ident = request.session['identity']['PSU_UUID']
    
    if request.session['supernag'] is True and request.session['opt-out'] is False:
        return {'status' : 'Error', 'message' : "<p>You must provide password reset information to continue.</p>"}
    
    if form.is_valid():
        UserDataItem.objects.filter(psu_uuid = ident).filter(key_name = 'PSU_EMPLOYEE_TITLE'). \
        update(key_valu = form.cleaned_data['job_title'])
        
        UserDataItem.objects.filter(psu_uuid = ident).filter(key_name = 'PSU_EMPLOYEE_DEPARTMENT_NAME'). \
        update(key_valu = form.cleaned_data['department'])
        
        UserDataItem.objects.filter(psu_uuid = ident).filter(key_name = 'PSU_EMPLOYEE_OFFICE_INFO'). \
        update(key_valu = form.cleaned_data['office_location'])
        
        return {'status' : 'Success', 'message' : '<p>Directory information updated successfully.</p>'}
    
    return {'status' : 'Error', 'message' : error_state_to_html(form)}

@login_required
def toggle_password_opt_out(request):
    request.session["opt-out"] = not request.session["opt-out"]

# A mapping of field names to DB keys.
keys = {
    'alternate_email' : 'EXTERNAL_EMAIL_ADDRESS',
    'cell_number' : 'CELL_PHONE_NUMBER',
    'cell_carrier' : 'CELL_PHONE_CARRIER',
    'job_title' : 'PSU_EMPLOYEE_TITLE',
    'department' : 'PSU_EMPLOYEE_DEPARTMENT_NAME',
    'office_location' : 'PSU_EMPLOYEE_OFFICE_INFO',
}

# This function is called by the delete ajax call. It is important that we be careful with accepted values.
@login_required
def delete_key_value(request):
    if request.POST['key'] not in keys:
        raise SuspiciousOperation
    
    UserDataItem.objects.filter(psu_uuid = request.session['identity']['PSU_UUID']).filter(key_name = keys[request.POST['key']]).delete()
    
    logger.info("Delete key: {} for {}".format(keys[request.POST['key']], request.session['identity']['PSU_UUID']))