export interface Questionnaire {
    id: string;
    business_profile_id: string;
    client_name: string;
    product_description?: string;
    problem_statement?: string;
    competitive_differentiation?: string;
    competitors?: string[];
    target_icp?: string;
    marketing_channels?: string[];
    business_objectives?: string;
    budget_range?: string;
    timeline?: string;
    created_at: string;
    updated_at: string;
}

export interface QuestionnaireCreate {
    business_profile_id: string;
    client_name?: string;
    product_description?: string;
    problem_statement?: string;
    competitive_differentiation?: string;
    competitors?: string[];
    target_icp?: string;
    marketing_channels?: string[];
    business_objectives?: string;
    budget_range?: string;
    timeline?: string;
}

export interface QuestionnaireUpdate extends Partial<QuestionnaireCreate> { }
