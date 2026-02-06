export interface BusinessProfile {
    id: string;
    user_id: string;
    business_name: string;
    website?: string;
    industry?: string;
    problems_solving: string[];
    target_customers: string[];
    products: string[];
    customer_stages: string[];
    trigger_events: string[];
    created_at: string;
    updated_at: string;
}

export interface BusinessProfileCreate {
    business_name: string;
    website?: string;
    industry?: string;
    problems_solving: string[];
    target_customers: string[];
    products: string[];
    customer_stages: string[];
    trigger_events: string[];
}

export interface BusinessProfileUpdate extends Partial<BusinessProfileCreate> { }
