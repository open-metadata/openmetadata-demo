const staticUsers = [
  {
    email: 'admin@open-metadata.org',
    displayName: 'Admin Super User',
    domain: 'Finance'
  },
  {
    email: 'aaron_johnson0@gmail.com',
    displayName: 'Aaron Johnson',
    domain: 'Marketing'
  },
  {
    email: 'brian_smith7@gmail.com',
    displayName: 'Brian Smith',
    domain: 'Finance'
  }
];

const resolvers = {
  Query: {
    users: () => staticUsers,
    user: (parent, args) => {
      return staticUsers.find(user => user.email === args.email);
    }
  }
};

module.exports = resolvers;