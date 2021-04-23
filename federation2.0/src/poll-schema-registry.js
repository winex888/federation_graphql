const { get } = require('lodash');
const request = require('request-promise-native');

exports.getServiceListWithTypeDefs = async () => {

	const serviceTypeDefinitions = await request({
		baseUrl: `http://${process.env.SCHEMA_REGESTRY_HOST}:${process.env.SCHEMA_REGESTRY_PORT}`,
		//baseUrl: `http://localhost:8310`,
		method: 'GET',
		url: process.env.SCHEMA_REGESTRY_URL,
		//url: '/schema',
		json: true,
	});

	return get(serviceTypeDefinitions, 'data', []).map((schema) => {
		return {
			name: schema.service_name,
			url: `http://${schema.host}:${schema.port}${schema.endpoint}`,
			version: 'v1',
			typeDefs: schema.graphql_schema,
		};
	});
};
