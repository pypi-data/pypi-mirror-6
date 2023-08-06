from .forms import EnquiryForm


def contact_form(request):
    """
    This inserts a contact form into every page (for the footer), and optionally processes
    the form if required.
    """

    success = False
    error = False

    if request.method == "POST":
        contact_form = EnquiryForm(request.POST)
        if contact_form.is_valid():
            success = True
            enquiry = contact_form.save(ip=request.META['REMOTE_ADDR'])
            enquiry.send()
            contact_form = EnquiryForm()
        else:
            error = True
    else:
        contact_form = EnquiryForm()

    return {'contact_form_success': success, 'contact_form_error': error, 'contact_form': contact_form}