import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:9000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface ProveRequest {
  proposition1: string;
  proposition2: string;
  method: 'automatic' | 'direct' | 'contrapositive' | 'absurd' | 'bidirectional';
  max_iterations: number;
  allow_bidirectional: boolean;
  verbose: boolean;
}

export interface Transformation {
  iteration: number;
  proposition: number;
  law: string;
  result: string;
  guided_by_nn: boolean;
  subexpression: string;
  p1: string;
  p2: string;
}

export interface TruthTableRow {
  values: Record<string, boolean>;
  subvalues_p1: Record<string, boolean>;
  subvalues_p2: Record<string, boolean>;
  p1: boolean;
  p2: boolean;
}

export interface TruthTable {
  variables: string[];
  subexpressions_p1: string[];
  subexpressions_p2: string[];
  rows: TruthTableRow[];
}

export interface ProveResponse {
  success: boolean;
  equivalent: boolean;
  method_used: string;
  iterations: number;
  nn_predictions: number;
  proposition1_initial: string;
  proposition2_initial: string;
  proposition1_final: string;
  proposition2_final: string;
  transformations: Transformation[];
  truth_table: TruthTable;
  message: string;
}

export interface StatusResponse {
  status: string;
  modelos_carregados: boolean;
  versao: string;
}

export interface SyntaxResponse {
  operadores: {
    negacao: string[];
    conjuncao: string[];
    disjuncao: string[];
    implicacao: string[];
  };
  constantes: {
    verdadeiro: string;
    falso: string;
  };
  agrupamento: string;
  exemplos: string[];
}

export interface MethodsResponse {
  metodos: {
    [key: string]: {
      descricao: string;
      objetivo?: string;
      estrategias?: string[];
    };
  };
}

export const proverService = {
  async prove(data: ProveRequest): Promise<ProveResponse> {
    const response = await api.post<ProveResponse>('/prove', data);
    return response.data;
  },

  async getStatus(): Promise<StatusResponse> {
    const response = await api.get<StatusResponse>('/status');
    return response.data;
  },

  async getSyntax(): Promise<SyntaxResponse> {
    const response = await api.get<SyntaxResponse>('/syntax');
    return response.data;
  },

  async getMethods(): Promise<MethodsResponse> {
    const response = await api.get<MethodsResponse>('/methods');
    return response.data;
  },
};

export default api;
