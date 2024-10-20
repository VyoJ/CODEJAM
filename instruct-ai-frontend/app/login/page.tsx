// "use client";

// import { FormEvent, useState } from "react";
// import { signIn } from "next-auth/react";
// import { useRouter } from "next/navigation";
// import Link from "next/link";

// export default function Login() {
//   const [error, setError] = useState("");
//   const router = useRouter();

//   const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
//     event.preventDefault();
//     const formData = new FormData(event.currentTarget);
//     const res = await signIn("credentials", {
//       email: formData.get("email"),
//       password: formData.get("password"),
//       redirect: false,
//     });
//     if (res?.error) {
//       setError(res.error as string);
//     }
//     if (res?.ok) {
//       return router.push("/");
//     }
//   };

//   return (
//     <section className="w-full h-screen flex items-center justify-center">
//       <form
//         className="p-6 w-full max-w-[400px] flex flex-col justify-between items-center gap-2
//         border border-solid border-black bg-white rounded"
//         onSubmit={handleSubmit}
//       >
//         {error && <div className="text-black">{error}</div>}
//         <h1 className="mb-5 w-full text-2xl font-bold">Sign In</h1>
//         <label className="w-full text-sm">Email</label>
//         <input
//           type="email"
//           placeholder="Email"
//           className="w-full h-8 border border-solid border-black rounded p-2"
//           name="email"
//         />
//         <label className="w-full text-sm">Password</label>
//         <div className="flex w-full">
//           <input
//             type="password"
//             placeholder="Password"
//             className="w-full h-8 border border-solid border-black rounded p-2"
//             name="password"
//           />
//         </div>
//         <button className="w-full border border-solid border-black rounded">
//           Sign In
//         </button>

//         <Link
//           href="/register"
//           className="text-sm text-[#888] transition duration-150 ease hover:text-black"
//         >
//           Don't have an account?
//         </Link>
//       </form>
//     </section>
//   );
// }

"use client";

import { FormEvent, useState } from "react";
import { signIn } from "next-auth/react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";

export default function Login() {
  const [error, setError] = useState("");
  const router = useRouter();

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const res = await signIn("credentials", {
      email: formData.get("email"),
      password: formData.get("password"),
      redirect: false,
    });
    if (res?.error) {
      setError(res.error as string);
    }
    if (res?.ok) {
      return router.push("/");
    }
  };

  return (
    <section className="w-full min-h-[calc(100vh-126px)] flex items-center justify-center bg-gradient-to-b from-background to-secondary p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl font-bold">Sign In</CardTitle>
          <CardDescription>
            Enter your credentials to access your account
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="Email"
                name="email"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Password"
                name="password"
                required
              />
            </div>
          </CardContent>
          <CardFooter className="flex flex-col space-y-4">
            <Button type="submit" className="w-full">
              Sign In
            </Button>
            <Link
              href="/register"
              className="text-sm text-muted-foreground transition duration-150 ease-in-out hover:text-primary"
            >
              Don't have an account?
            </Link>
          </CardFooter>
        </form>
      </Card>
    </section>
  );
}
