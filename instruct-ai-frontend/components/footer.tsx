import Link from "next/link";

export function Footer() {
  return (
    <footer className="border-t h-14 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="p-4 flex flex-col items-center justify-between">
        <p className="text-center text-sm leading-loose text-muted-foreground">
          Built by Team TARS for CODEJAM. The source code is available on{" "}
          <Link
            href="https://github.com/VyoJ/CODEJAM_instruct_ai"
            target="_blank"
            rel="noreferrer"
            className="font-medium underline underline-offset-4"
          >
            GitHub
          </Link>
          .
        </p>
      </div>
    </footer>
  );
}
