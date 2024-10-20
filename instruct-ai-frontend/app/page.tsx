import Link from "next/link";
import { Button } from "@/components/ui/button";
import { BackgroundBeamsWithCollision } from "@/components/background-beams";

export default function Home() {
  return (
    <BackgroundBeamsWithCollision>
        <div className="flex flex-col sm:flex-row justify-center gap-4 pt-8 items-center">
          <Button
            asChild
            size="lg"
            variant="secondary"
            className="md:text-lg max-w-sm"
          >
            <Link href="/assessment">Try Demo</Link>
          </Button>
        </div>
      
    </BackgroundBeamsWithCollision>
  );
}