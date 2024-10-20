import Link from "next/link";
import { Button } from "@/components/ui/button";
import { BackgroundBeamsWithCollision } from "@/components/background-beams";

export default function Home() {
  return (
    <BackgroundBeamsWithCollision>
      <div className="flex flex-col sm:flex-row justify-center gap-4 pt-8 items-center">
        <h2 className="text-2xl relative z-20 md:text-4xl lg:text-7xl font-bold text-center text-black dark:text-white font-sans">
          Want to prepare for exams and placements?{" "}
          <div className="relative mx-auto inline-block w-max [filter:drop-shadow(0px_1px_3px_rgba(27,_37,_80,_0.14))]">
            <div className="absolute left-0 bg-clip-text bg-no-repeat text-transparent bg-gradient-to-r py-4 from-purple-500 via-violet-500 to-pink-500 [text-shadow:0_0_rgba(0,0,0,0.1)]">
              <span>Instruct AI</span>
            </div>
            <div className="relative bg-clip-text text-transparent bg-no-repeat bg-gradient-to-r from-purple-500 via-violet-500 to-pink-500 py-4">
              <span>Instruct AI</span>
            </div>
          </div>
          <div className="flex flex-col sm:flex-row justify-center gap-4 pt-8 items-center">
            <Button
              asChild
              size="lg"
              variant="outline"
              className="md:text-lg max-w-sm"
            >
              <Link href="/assessment">Try our Platform</Link>
            </Button>
          </div>
        </h2>
      </div>
    </BackgroundBeamsWithCollision>
  );
}
