from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
import logging

logger = logging.getLogger('prod')


class SocialAccountAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        provider = sociallogin.account.provider

        request.session['provider'] = provider
        logger.info(f"✅ allauth Adapter: 세션에 프로바이더 '{provider}' 저장 완료!")

        return super().pre_social_login(request, sociallogin)
