import graphene


from apps.api.graphql.v1.queries import auth as authQueries
from apps.api.graphql.v1.queries import business as businessQueries
from apps.api.graphql.v1.queries import category as categoryQueries
from apps.api.graphql.v1.queries import order as orderQueries
from apps.api.graphql.v1.queries import product as productQueries
from apps.api.graphql.v1.queries import marketing as marketingQueries
from apps.api.graphql.v1.queries import client as clientQueries
from apps.api.graphql.v1.queries import employee as employeeQueries
from apps.api.graphql.v1.queries import branch as branchQueries
from apps.api.graphql.v1.queries import role as roleQueries
from apps.api.graphql.v1.queries import delivery as deliveryQueries
from apps.api.graphql.v1.queries import inventory as inventoryQueries


from apps.api.graphql.v1.mutations import auth
from apps.api.graphql.v1.mutations import order
from apps.api.graphql.v1.mutations import business
from apps.api.graphql.v1.mutations import category
from apps.api.graphql.v1.mutations import product
from apps.api.graphql.v1.mutations import client
from apps.api.graphql.v1.mutations import membership
from apps.api.graphql.v1.mutations import marketing
from apps.api.graphql.v1.mutations import branch
from apps.api.graphql.v1.mutations import employee
from apps.api.graphql.v1.mutations import role
from apps.api.graphql.v1.mutations import delivery
from apps.api.graphql.v1.mutations import cards
from apps.api.graphql.v1.mutations import topup
from apps.api.graphql.v1.mutations import image

# from apps.api.graphql.v1.queries.user_queries import UserQuery
# from apps.api.graphql.v1.mutations.user_mutations import CreateUser


class Query(
        authQueries.Query,
        businessQueries.Query,
        categoryQueries.Query,
        marketingQueries.Query,
        orderQueries.Query,
        productQueries.Query,
        clientQueries.Query,
        employeeQueries.Query,
        branchQueries.Query,
        roleQueries.Query,
        deliveryQueries.Query,
        inventoryQueries.Query,
        graphene.ObjectType
    ):
    pass

class Mutation(
        auth.Mutation,
        order.Mutation,
        business.Mutation,
        category.Mutation,
        product.Mutation,
        client.Mutation,
        membership.Mutation,
        marketing.Mutation,
        branch.Mutation,
        employee.Mutation,
        role.Mutation,
        delivery.Mutation,
        cards.Mutation,
        topup.Mutation,
        image.Mutation,
        graphene.ObjectType
    ):

    pass


schema = graphene.Schema(query=Query, mutation=Mutation)