import type { NextConfig } from "next";

const isGithubPages = process.env.GITHUB_PAGES === "true";
const repositoryName = process.env.NEXT_PUBLIC_GITHUB_PAGES_REPOSITORY ?? "";

const basePath = isGithubPages && repositoryName ? `/${repositoryName}` : "";

const nextConfig: NextConfig = {
    output: "export",
    trailingSlash: true,
    basePath,
    assetPrefix: basePath || undefined,
    images: {
        unoptimized: true,
    },
};

export default nextConfig;