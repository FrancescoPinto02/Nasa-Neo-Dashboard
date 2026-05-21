"use client";

import { useEffect, useState } from "react";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";

import { NeoCloseApproachesTable } from "@/components/neos/NeoCloseApproachesTable";
import { NeoDetailsHero } from "@/components/neos/NeoDetailsHero";
import { NeoOrbitCard } from "@/components/neos/NeoOrbitCard";
import { Button } from "@/components/ui/Button";
import { LoadingState } from "@/components/ui/LoadingState";
import { ApiClientError } from "@/lib/api/client";
import { getNeoDetails } from "@/lib/api/neos";
import type { NeoDetailsResponse } from "@/types/neo";

export default function NeoDetailsPage() {
    const params = useParams();

    const neoId = String(params.neoId);

    const [neo, setNeo] = useState<NeoDetailsResponse | null>(null);

    const [isLoading, setIsLoading] = useState(true);
    const [errorMessage, setErrorMessage] = useState<string | null>(null);

    useEffect(() => {
        async function loadNeoDetails() {
            setIsLoading(true);
            setErrorMessage(null);

            try {
                const response = await getNeoDetails(neoId);
                setNeo(response);
            } catch (error) {
                if (error instanceof ApiClientError) {
                    setErrorMessage(error.message);
                } else {
                    setErrorMessage("Si è verificato un errore imprevisto.");
                }
            } finally {
                setIsLoading(false);
            }
        }

        void loadNeoDetails();
    }, [neoId]);

    return (
        <main className="min-h-screen overflow-hidden bg-slate-950">
            <div className="pointer-events-none fixed inset-0">
                <div className="absolute left-[-10%] top-[-10%] h-96 w-96 rounded-full bg-blue-500/30 blur-3xl" />
                <div className="absolute right-[-10%] top-[10%] h-96 w-96 rounded-full bg-violet-500/25 blur-3xl" />
            </div>

            <div className="relative mx-auto flex w-full max-w-7xl flex-col gap-6 px-4 py-8 sm:px-6 lg:px-8">
                <div>
                    <Link href="/">
                        <Button variant="secondary" className="gap-2">
                            <ArrowLeft className="h-4 w-4" />
                            Torna alla dashboard
                        </Button>
                    </Link>
                </div>

                {errorMessage ? (
                    <div className="rounded-3xl border border-rose-300/60 bg-rose-50/95 p-5 text-sm text-rose-800 shadow-xl shadow-rose-950/10">
                        <p className="font-bold">Errore durante il caricamento</p>
                        <p className="mt-1">{errorMessage}</p>
                    </div>
                ) : null}

                {isLoading ? (
                    <LoadingState />
                ) : neo ? (
                    <>
                        <NeoDetailsHero neo={neo} />
                        <NeoOrbitCard orbitalData={neo.orbital_data} />
                        <NeoCloseApproachesTable
                            approaches={neo.close_approaches}
                        />
                    </>
                ) : null}
            </div>
        </main>
    );
}