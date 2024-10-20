import Link from "next/link";

export function Footer() {
  return (
    <footer className="border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="p-4 flex flex-col items-center justify-between">
        <p className="text-center text-sm leading-loose text-muted-foreground">
          Built by{" "}
          <Link
            href="https://www.linkedin.com/in/samarth-prakash/"
            target="_blank"
            rel="noreferrer"
            className="font-medium underline underline-offset-4"
          >
            Samarth
          </Link>{" "}
          and{" "}
          <Link
            href="https://www.linkedin.com/in/vyomanjain"
            target="_blank"
            rel="noreferrer"
            className="font-medium underline underline-offset-4"
          >
            Vyoman
          </Link>
          . The source code is available on{" "}
          <Link
            href="https://github.com/RAGsToRichAIs-PESU-IO/agent-interact"
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