import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
  client: 'axios',
  input: '../Backend/openapi_spec.json',
  output: './src/client',
});