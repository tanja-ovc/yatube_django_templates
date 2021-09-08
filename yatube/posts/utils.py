from .models import Follow


def add_context_to_post_and_profile(request, a_user, context):

    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=a_user
        ).exists()
        authenticated_user = True

        context['following'] = following
        context['authenticated_user'] = authenticated_user

    if request.user == a_user:
        self_following = True
        editing_permitted = True

        context['self_following'] = self_following
        context['editing_permitted'] = editing_permitted
