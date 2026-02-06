"use client";

import { useEffect, useState } from "react";
import { useForm, useFieldArray } from "react-hook-form";
import { useRouter } from "next/navigation";
import { createQuestionnaire } from "@/lib/api/questionnaires";
import { getProfiles } from "@/lib/api/profiles";
import { BusinessProfile } from "@/types/profile";
import { QuestionnaireCreate } from "@/types/questionnaire";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "../ui/textarea";

export function QuestionnaireForm() {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(false);
    const [profiles, setProfiles] = useState<BusinessProfile[]>([]);

    useEffect(() => {
        getProfiles().then(setProfiles).catch(console.error);
    }, []);

    // Default values
    const { register, control, handleSubmit, formState: { errors }, watch } = useForm<QuestionnaireCreate>({
        defaultValues: {
            business_profile_id: "",
            client_name: "",
            product_description: "",
            problem_statement: "",
            competitive_differentiation: "",
            competitors: [""],
            target_icp: "",
            marketing_channels: [], // Should be checkboxes really
            business_objectives: "",
            budget_range: "",
            timeline: ""
        }
    });

    const { fields: competitorFields, append: appendCompetitor, remove: removeCompetitor } = useFieldArray({
        control,
        name: "competitors"
    });

    const onSubmit = async (data: QuestionnaireCreate) => {
        setIsLoading(true);
        try {
            await createQuestionnaire(data);
            router.push("/dashboard/questionnaires");
            router.refresh();
        } catch (error) {
            console.error("Failed to create questionnaire:", error);
            alert("Failed to create questionnaire.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit(onSubmit)} className="max-w-3xl mx-auto py-8">
            <Card>
                <CardHeader>
                    <CardTitle>Create Strategy Questionnaire</CardTitle>
                    <CardDescription>
                        Capture specific goals and context for a new marketing strategy.
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    <div className="space-y-2">
                        <Label htmlFor="business_profile_id">Select Business Profile</Label>
                        <div className="relative">
                            <select
                                {...register("business_profile_id", { required: true })}
                                className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 appearance-none"
                            >
                                <option value="">Select a profile...</option>
                                {profiles.map(p => (
                                    <option key={p.id} value={p.id}>{p.business_name}</option>
                                ))}
                            </select>
                            <div className="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none text-muted-foreground">
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m6 9 6 6 6-6" /></svg>
                            </div>
                        </div>
                        {errors.business_profile_id && <span className="text-destructive text-xs">Profile is required</span>}
                        {profiles.length === 0 && <p className="text-xs text-muted-foreground">No profiles found. <a href="/dashboard/profiles/new" className="underline text-primary">Create one first.</a></p>}
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="client_name">Client Name (Optional)</Label>
                            <Input id="client_name" {...register("client_name")} placeholder="Specific Client or Campaign Name" />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="budget_range">Budget Range</Label>
                            <Input id="budget_range" {...register("budget_range")} placeholder="$2,000 - $5,000 / month" />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="product_description">Product/Service Focus</Label>
                        <Textarea id="product_description" {...register("product_description")} placeholder="What specific product are we promoting?" />
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="business_objectives">Business Objectives</Label>
                        <Textarea id="business_objectives" {...register("business_objectives")} placeholder="What are the key goals? (e.g. 100 leads/month, Brand Awareness)" />
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="target_icp">Ideal Customer Profile (ICP)</Label>
                        <Textarea id="target_icp" {...register("target_icp")} placeholder="Describe the perfect customer for this campaign." />
                    </div>

                    <div className="space-y-2">
                        <Label>Competitors</Label>
                        {competitorFields.map((field, index) => (
                            <div key={field.id} className="flex gap-2 mb-2">
                                <Input {...register(`competitors.${index}` as any)} placeholder="Competitor Name/URL" />
                                <Button type="button" variant="outline" size="icon" onClick={() => removeCompetitor(index)}>&times;</Button>
                            </div>
                        ))}
                        <Button type="button" variant="ghost" size="sm" onClick={() => {
                            // @ts-ignore
                            appendCompetitor("")
                        }}>+ Add Competitor</Button>
                    </div>

                </CardContent>
                <CardFooter className="flex justify-end gap-4">
                    <Button variant="outline" type="button" onClick={() => router.back()}>Cancel</Button>
                    <Button type="submit" disabled={isLoading}>
                        {isLoading ? "Saving..." : "Create Questionnaire"}
                    </Button>
                </CardFooter>
            </Card>
        </form>
    );
}
