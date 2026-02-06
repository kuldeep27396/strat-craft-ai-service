export interface StrategySection {
    heading: string;
    content: string;
    tactics: string[];
    kpis: string[];
}

export interface StrategyContent {
    title: string;
    sections: StrategySection[];
    pricing?: {
        monthly_cost: number;
        team: string[];
    };
}

export interface Strategy {
    id: string;
    questionnaire_id: string;
    strategy_content: StrategyContent;
    status: 'generating' | 'completed' | 'failed';
    version: number;
    created_at: string;
    updated_at: string;
}

export interface StrategyCreate {
    questionnaire_id: string;
}
