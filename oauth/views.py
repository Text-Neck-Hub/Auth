from django.shortcuts import render

# Create your views here.


def google_oauth_callback(request):
    """
    Handle the Google OAuth callback.
    This view is called after the user has authenticated with Google.
    """
    # You can access the user's information from the request object
    user = request.user
    print('s')
    # Render a template or redirect to another page
    return render(request, 'oauth/callback.html', {'user': user})
