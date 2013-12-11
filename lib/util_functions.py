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
