const { gql } = require('graphql-tag');

const typeDefs = gql`
  type User {
    email: String!
    displayName: String!
    domain: String!
  }

  type Query {
    users: [User!]!
    user(email: String!): User
  }
`;

module.exports = typeDefs;