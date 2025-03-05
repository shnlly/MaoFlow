interface Config {
  api: {
    host: string;
    port: number;
    baseUrl: string;
    apiPrefix: string;
  };
}

const isDev = process.env.NODE_ENV === 'development';

const config: Config = {
  api: {
    host: isDev ? 'localhost' : 'localhost', // 在生产环境中可能需要修改
    port: 17349,
    baseUrl: `http://localhost:17349`,
    apiPrefix: '/api/v1'
  }
};

export const API_BASE_URL = config.api.baseUrl;
export const API_PREFIX = config.api.apiPrefix;
export const API_PORT = config.api.port;

export default config; 