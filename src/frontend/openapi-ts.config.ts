import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
  client: 'axios',
  input: '../Backend/openapi.json',  // OpenAPI spec generated from Backend
  output: './src/client',
});
