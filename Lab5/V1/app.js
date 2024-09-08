import { createYoga, createSchema } from 'graphql-yoga';
import { createServer } from 'http';
import sqlite3 from 'sqlite3';

const db = new sqlite3.Database('./database.db');

db.serialize(() => {
  db.run("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT)");
});

const typeDefs = `
  type User {
    id: ID!
    name: String!
    email: String!
  }

  type Query {
    users: [User!]
    user(id: ID!): User
  }

  type Mutation {
    createUser(name: String!, email: String!): User!
    updateUser(id: ID!, name: String, email: String): User
    deleteUser(id: ID!): String
  }
`;

const resolvers = {
  Query: {
    users: () => {
      return new Promise((resolve, reject) => {
        db.all("SELECT * FROM users", [], (err, rows) => {
          if (err) {
            reject(err);
          } else {
            resolve(rows);
          }
        });
      });
    },
    user: (_, { id }) => {
      return new Promise((resolve, reject) => {
        db.get("SELECT * FROM users WHERE id = ?", [id], (err, row) => {
          if (err) {
            reject(err);
          } else {
            resolve(row);
          }
        });
      });
    },
  },
  Mutation: {
    createUser: (_, { name, email }) => {
      return new Promise((resolve, reject) => {
        db.run("INSERT INTO users (name, email) VALUES (?, ?)", [name, email], function (err) {
          if (err) {
            reject(err);
          } else {
            resolve({ id: this.lastID, name, email });
          }
        });
      });
    },
    updateUser: (_, { id, name, email }) => {
      return new Promise((resolve, reject) => {
        db.run(
          "UPDATE users SET name = ?, email = ? WHERE id = ?",
          [name, email, id],
          function (err) {
            if (err) {
              reject(err);
            } else {
              resolve({ id, name, email });
            }
          }
        );
      });
    },
    deleteUser: (_, { id }) => {
      return new Promise((resolve, reject) => {
        db.run("DELETE FROM users WHERE id = ?", [id], function (err) {
          if (err) {
            reject(err);
          } else if (this.changes === 0) {
            resolve("No user found");
          } else {
            resolve(`User with ID ${id} deleted`);
          }
        });
      });
    },
  },
};

const yoga = createYoga({
  schema: createSchema({
    typeDefs,
    resolvers,
  }),
});

const server = createServer(yoga);

server.listen(4000, () => {
  console.log('Server is running on http://localhost:4000/graphql');
});

