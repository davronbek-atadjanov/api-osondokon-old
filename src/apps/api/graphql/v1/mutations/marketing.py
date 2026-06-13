import graphene

from apps.api.graphql.v1.types.marketing import BannerType
from apps.marketing.models import Banner
from apps.business.models import Business
from django.core.exceptions import ObjectDoesNotExist


class CreateBanner(graphene.Mutation):
    class Arguments:
        image = graphene.String(required=True)
        desktop_image = graphene.String(required=True)
        business_id = graphene.String(required=True)
        link = graphene.String()

    banner = graphene.Field(BannerType)

    def mutate(self, info, image, desktop_image, business_id, link=None):
        # Fetch the business object
        business = Business.objects.get(hash_id=business_id)

        # Check the business plan
        if plan := business.plan:
            count = Banner.objects.filter(business=business).count()

            # Improved logic for plan limits
            if plan == "BASIC" and count >= 1:
                raise Exception("Basic plan allows only 1 banner.")
            if plan == "PRO" and count >= 5:
                raise Exception("Professional plan allows up to 5 banners.")
            if plan == "ENTERPRISE" and count >= 10:
                raise Exception("Enterprise plan allows up to 10 banners.")

            # If none of the conditions raise an exception, create the banner
            banner = Banner.objects.create(
                image=image, desktop_image=desktop_image, link=link, business=business)

            return CreateBanner(banner=banner)

        else:
            raise Exception("Business does not have a valid plan")


class UpdateBanner(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        image = graphene.String(required=True)
        desktop_image = graphene.String(required=True)
        link = graphene.String()

    banner = graphene.Field(BannerType)

    def mutate(self, info, id, image=None, desktop_image=None, link=None):
        try:
            banner = Banner.objects.get(pk=id)
        except ObjectDoesNotExist:
            raise Exception("Banner not found")

        if image:
            banner.image = image

        if desktop_image:
            banner.desktop_image = desktop_image
        
        if link:
            banner.link = link

        banner.save()
        return UpdateBanner(banner=banner)


class DeleteBanner(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        try:
            banner = Banner.objects.get(pk=id)
            banner.delete()
            return DeleteBanner(success=True)
        except ObjectDoesNotExist:
            return DeleteBanner(success=False)


class Mutation(graphene.ObjectType):
    create_banner = CreateBanner.Field()
    update_banner = UpdateBanner.Field()
    delete_banner = DeleteBanner.Field()
