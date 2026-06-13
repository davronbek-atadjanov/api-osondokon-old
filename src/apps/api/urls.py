from django.urls import path
from django.views.decorators.csrf import csrf_exempt
# from graphene_django.views import GraphQLView
from graphene_file_upload.django import FileUploadGraphQLView
from apps.api.graphql.v1.schema import schema

urlpatterns = [
    path("gql/v1/", csrf_exempt(FileUploadGraphQLView.as_view(graphiql=True, schema=schema))),
]