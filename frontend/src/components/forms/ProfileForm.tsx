"use client";

import { useState } from "react";
import { useForm, useFieldArray } from "react-hook-form";
import { useRouter } from "next/navigation";
import { createProfile } from "@/lib/api/profiles";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { BusinessProfileCreate } from "@/types/profile";

export function ProfileForm() {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(false);

    // Default values
    const { register, control, handleSubmit, formState: { errors } } = useForm<BusinessProfileCreate>({
        defaultValues: {
            business_name: "",
            website: "",
            industry: "",
            problems_solving: [""],
            products: [""],
            target_customers: [""],
            customer_stages: ["Awareness", "Consideration", "Decision"],
            trigger_events: [""]
        }
    });

    // Helper to manage dynamic arrays
    const renderArrayField = (name: any, label: string, placeholder: string) => {
        const { fields, append, remove } = useFieldArray({
            control,
            // @ts-ignore
            name: name
        });

        return (
            <div className="space-y-2">
                <Label>{label}</Label>
                {fields.map((field, index) => (
                    <div key={field.id} className="flex gap-2">
                        <Input
                            {...register(`${name}.${index}` as any, { required: true })}
                            placeholder={placeholder}
                        />
                        <Button
                            type="button"
                            variant="outline"
                            size="icon"
                            onClick={() => remove(index)}
                            disabled={fields.length === 1 && index === 0}
                        >
                            &times;
                        </Button>
                    </div>
                ))}
                <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="mt-1"
                    onClick={() => append("")}
                >
                    + Add {label}
                </Button>
            </div>
        );
    };

    const onSubmit = async (data: BusinessProfileCreate) => {
        setIsLoading(true);
        try {
            await createProfile(data);
            router.push("/dashboard/profiles");
            router.refresh();
        } catch (error) {
            console.error("Failed to create profile:", error);
            alert("Failed to create profile. Please check the backend connection.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit(onSubmit)} className="max-w-3xl mx-auto py-8">
            <Card>
                <CardHeader>
                    <CardTitle>Create Business Profile</CardTitle>
                    <CardDescription>
                        Define your business context once and reuse it for all client strategies.
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="business_name">Business Name</Label>
                            <Input id="business_name" {...register("business_name", { required: true })} placeholder="Acme Agency" />
                            {errors.business_name && <span className="text-red-500 text-xs">Required</span>}
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="industry">Industry</Label>
                            <Input id="industry" {...register("industry")} placeholder="Digital Marketing" />
                        </div>
                        <div className="space-y-2 md:col-span-2">
                            <Label htmlFor="website">Website</Label>
                            <Input id="website" {...register("website")} placeholder="https://example.com" />
                        </div>
                    </div>

                    <div className="grid grid-cols-1 gap-6">
                        {renderArrayField("products", "Products / Services", "e.g. SEO Audit, Content Marketing")}
                        {renderArrayField("target_customers", "Target Customer Segments", "e.g. SaaS Founders, E-commerce CMOS")}
                        {renderArrayField("problems_solving", "Problems You Solve", "e.g. Low organic traffic, Poor conversion rates")}
                        {renderArrayField("trigger_events", "Trigger Events (Why they buy)", "e.g. Funding round, Website migration")}
                    </div>
                </CardContent>
                <CardFooter className="flex justify-end gap-4">
                    <Button variant="outline" type="button" onClick={() => router.back()}>Cancel</Button>
                    <Button type="submit" disabled={isLoading}>
                        {isLoading ? "Saving..." : "Create Profile"}
                    </Button>
                </CardFooter>
            </Card>
        </form>
    );
}
