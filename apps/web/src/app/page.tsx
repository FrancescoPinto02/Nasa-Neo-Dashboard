"use client";

import { useEffect, useState } from "react";
import { Rocket, Satellite, Sparkles } from "lucide-react";

import { NeoCharts } from "@/components/neos/NeoCharts";
import { NeoFilters } from "@/components/neos/NeoFilters";
import { NeoStatsCards } from "@/components/neos/NeoStatsCards";
import { NeoTable } from "@/components/neos/NeoTable";
import { Badge } from "@/components/ui/Badge";
import { LoadingState } from "@/components/ui/LoadingState";
import { ApiClientError } from "@/lib/api/client";
import { getNeoFeed, getNeoStats } from "@/lib/api/neos";
import type {
  NeoFeedResponse,
  NeoSortBy,
  NeoStatsResponse,
  SortOrder,
} from "@/types/neo";

const DEFAULT_START_DATE = "2026-05-20";
const DEFAULT_END_DATE = "2026-05-26";

export default function HomePage() {
  const [startDate, setStartDate] = useState(DEFAULT_START_DATE);
  const [endDate, setEndDate] = useState(DEFAULT_END_DATE);
  const [hazardous, setHazardous] = useState("all");
  const [sortBy, setSortBy] = useState<NeoSortBy>("date");
  const [sortOrder, setSortOrder] = useState<SortOrder>("asc");

  const [feed, setFeed] = useState<NeoFeedResponse | null>(null);
  const [stats, setStats] = useState<NeoStatsResponse | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function fetchDashboardData() {
    const hazardousFilter = hazardous === "all" ? null : hazardous === "true";

    return Promise.all([
      getNeoFeed({
        startDate,
        endDate,
        hazardous: hazardousFilter,
        sortBy,
        sortOrder,
      }),
      getNeoStats({
        startDate,
        endDate,
      }),
    ]);
  }

  async function loadDashboardData() {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const [feedResponse, statsResponse] = await fetchDashboardData();

      setFeed(feedResponse);
      setStats(statsResponse);
    } catch (error) {
      setErrorMessage(getErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    let isMounted = true;

    async function loadInitialDashboardData() {
      try {
        const [feedResponse, statsResponse] = await fetchDashboardData();

        if (!isMounted) {
          return;
        }

        setFeed(feedResponse);
        setStats(statsResponse);
      } catch (error) {
        if (!isMounted) {
          return;
        }

        setErrorMessage(getErrorMessage(error));
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    void loadInitialDashboardData();

    return () => {
      isMounted = false;
    };

    // Carichiamo i dati iniziali una sola volta.
    // I filtri vengono applicati tramite submit del form.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
      <main className="min-h-screen overflow-hidden bg-slate-950 text-slate-950">
        <div className="pointer-events-none fixed inset-0">
          <div className="absolute left-[-10%] top-[-10%] h-96 w-96 rounded-full bg-blue-500/30 blur-3xl" />
          <div className="absolute right-[-10%] top-[10%] h-96 w-96 rounded-full bg-violet-500/25 blur-3xl" />
          <div className="absolute bottom-[-15%] left-[30%] h-96 w-96 rounded-full bg-cyan-500/20 blur-3xl" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(255,255,255,0.14),transparent_35%)]" />
        </div>

        <div className="relative mx-auto flex w-full max-w-7xl flex-col gap-6 px-4 py-8 sm:px-6 lg:px-8">
          <Hero />

          <NeoFilters
              startDate={startDate}
              endDate={endDate}
              hazardous={hazardous}
              sortBy={sortBy}
              sortOrder={sortOrder}
              isLoading={isLoading}
              onStartDateChange={setStartDate}
              onEndDateChange={setEndDate}
              onHazardousChange={setHazardous}
              onSortByChange={setSortBy}
              onSortOrderChange={setSortOrder}
              onSubmit={loadDashboardData}
          />

          {errorMessage ? (
              <div className="rounded-3xl border border-rose-300/60 bg-rose-50/95 p-5 text-sm text-rose-800 shadow-xl shadow-rose-950/10">
                <p className="font-bold">Errore durante il caricamento</p>
                <p className="mt-1">{errorMessage}</p>
              </div>
          ) : null}

          {isLoading ? (
              <LoadingState />
          ) : (
              <>
                {stats ? <NeoStatsCards stats={stats} /> : null}
                {stats ? <NeoCharts stats={stats} /> : null}
                {feed ? <NeoTable neos={feed.results} /> : null}
              </>
          )}
        </div>
      </main>
  );
}

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiClientError) {
    return error.message;
  }

  return "Si è verificato un errore imprevisto.";
}

function Hero() {
  return (
      <header className="relative overflow-hidden rounded-[2rem] border border-white/10 bg-white/[0.08] p-6 text-white shadow-2xl shadow-black/20 backdrop-blur md:p-8">
        <div className="absolute right-6 top-6 hidden rounded-full border border-white/10 bg-white/10 p-4 md:block">
          <Satellite className="h-10 w-10 text-cyan-200" />
        </div>

        <div className="max-w-3xl">
          <div className="mb-5 flex flex-wrap items-center gap-2">
            <Badge variant="default">
              <Sparkles className="h-3.5 w-3.5" />
              NASA NeoWs
            </Badge>

            <Badge variant="muted">
              <Rocket className="h-3.5 w-3.5" />
              FastAPI proxy
            </Badge>
          </div>

          <p className="text-sm font-bold uppercase tracking-[0.3em] text-cyan-200">
            Near Earth Objects
          </p>

          <h1 className="mt-3 max-w-2xl text-4xl font-black tracking-tight sm:text-5xl lg:text-6xl">
            Monitoraggio asteroidi vicino alla Terra
          </h1>

          <p className="mt-5 max-w-2xl text-base leading-7 text-slate-300">
            Analizza distanze, velocità, diametri stimati e rischio potenziale
            degli oggetti osservati da NASA NeoWs, con dati normalizzati dal
            backend FastAPI.
          </p>
        </div>
      </header>
  );
}