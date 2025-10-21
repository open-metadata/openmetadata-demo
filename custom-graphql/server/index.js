const { ApolloServer } = require('@apollo/server');
const { startStandaloneServer } = require('@apollo/server/standalone');
const typeDefs = require('./schema');
const resolvers = require('./resolvers');

async function startServer() {
  const server = new ApolloServer({
    typeDefs,
    resolvers,
  });

  const { url } = await startStandaloneServer(server, {
    listen: { port: 4000 },
  });

  console.log(`🚀 GraphQL server ready at ${url}`);
  console.log('Try querying:');
  console.log('- All users: { users { email displayName domain } }');
  console.log('- Specific user: { user(email: "admin@open-metadata.org") { email displayName domain } }');
}

startServer().catch(error => {
  console.error('Error starting server:', error);
});