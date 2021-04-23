const {ApolloServer} = require('apollo-server')
const {ApolloGateway} = require('@apollo/gateway')
const FileUploadDataSource = require("@profusion/apollo-federation-upload");

const { GraphQLObjectType, GraphQLSchema, GraphQLString } = require('graphql');
const CustomGateway = require('./custom-gateway');
const request = require('request')

console.log(process.env.PORT);
function getStatus(service) {
    return new Promise((resolve, reject) => {
        request(service.url, function(error, response, body) {
            const success = !error && !!response;
            if (!success) {
                console.log('>', service.url, 'is down')
                reject();
            }
            else resolve()
            // resolve({url: url.url, status: (!error && !!response) ? "OK": "Down"});
        });
    })
}

checkAvailability = function (urls) {
    let promiseList = urls.map(url => getStatus(url));

    return Promise.all(promiseList)
}
async function run() {
const serviceList = [];
  const loop = setInterval(() => {
    checkAvailability(serviceList).then(resultList => {

    const gateway = new CustomGateway({
        serviceList: [],
        debug: true,
        experimental_pollInterval: 10000, // 10 sec
        buildService: ({ url }) => new FileUploadDataSource.default({ url }),
    });

      const server = new ApolloServer({
        gateway,
        subscriptions: false
      });
      server.listen(process.env.PORT).then(({ url }) => {
        console.log(`🚀 Server ready at ${url}`);
      });
      clearInterval( loop );
    });
  }, 1000)
}


run().catch(console.log)