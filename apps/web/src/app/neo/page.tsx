import { Suspense } from "react";

import { NeoDetailsClient } from "@/components/neos/NeoDetailsClient";
import { LoadingState } from "@/components/ui/LoadingState";

export default function NeoPage() {
    return (
        <Suspense
            fallback={
                <main className="min-h-screen overflow-hidden bg-slate-950 px-4 py-8 sm:px-6 lg:px-8">
                    <div className="mx-auto max-w-7xl">
                        <LoadingState />
                    </div>
                </main>
            }
        >
            <NeoDetailsClient />
        </Suspense>
    );
}