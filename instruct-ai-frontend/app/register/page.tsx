// "use client";

// import { FormEvent, useRef, useState } from "react";
// import { useRouter } from "next/navigation";
// import Link from "next/link";
// import { register } from "../actions/register";

// export default function Register() {
//   const [error, setError] = useState<string>();
//   const router = useRouter();
//   const ref = useRef<HTMLFormElement>(null);

//   const handleSubmit = async (formData: FormData) => {
//     const r = await register({
//       email: formData.get("email"),
//       password: formData.get("password"),
//       name: formData.get("name"),
//     });
//     ref.current?.reset();
//     if (r?.error) {
//       setError(r.error);
//       return;
//     } else {
//       return router.push("/login");
//     }
//   };

//   return (
//     <section className="w-full h-screen flex items-center justify-center">
//       <form
//         ref={ref}
//         action={handleSubmit}
//         className="p-6 w-full max-w-[400px] flex flex-col justify-between items-center gap-2
//             border border-solid border-black bg-white rounded"
//       >
//         {error && <div className="">{error}</div>}
//         <h1 className="mb-5 w-full text-2xl font-bold">Register</h1>

//         <label className="w-full text-sm">Full Name</label>
//         <input
//           type="text"
//           placeholder="Full Name"
//           className="w-full h-8 border border-solid border-black py-1 px-2.5 rounded text-[13px]"
//           name="name"
//         />

//         <label className="w-full text-sm">Email</label>
//         <input
//           type="email"
//           placeholder="Email"
//           className="w-full h-8 border border-solid border-black py-1 px-2.5 rounded"
//           name="email"
//         />

//         <label className="w-full text-sm">Password</label>
//         <div className="flex w-full">
//           <input
//             type="password"
//             placeholder="Password"
//             className="w-full h-8 border border-solid border-black py-1 px-2.5 rounded"
//             name="password"
//           />
//         </div>

//         <button
//           className="w-full border border-solid border-black py-1.5 mt-2.5 rounded
//             transition duration-150 ease hover:bg-black"
//         >
//           Sign up
//         </button>

//         <Link
//           href="/login"
//           className="text-sm text-[#888] transition duration-150 ease hover:text-black"
//         >
//           Already have an account?
//         </Link>
//       </form>
//     </section>
//   );
// }

"use client";

import { FormEvent, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { register } from "../actions/register";
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

export default function Register() {
  const [error, setError] = useState<string>();
  const router = useRouter();
  const ref = useRef<HTMLFormElement>(null);

  const handleSubmit = async (formData: FormData) => {
    const r = await register({
      email: formData.get("email") as string,
      password: formData.get("password") as string,
      name: formData.get("name") as string,
    });
    ref.current?.reset();
    if (r?.error) {
      setError(r.error);
      return;
    } else {
      return router.push("/login");
    }
  };

  return (
    <section className="w-full min-h-[calc(100vh-126px)] flex items-center justify-center bg-gradient-to-b from-background to-secondary p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl font-bold">Register</CardTitle>
          <CardDescription>Create a new account to get started</CardDescription>
        </CardHeader>
        <form ref={ref} action={handleSubmit}>
          <CardContent className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            <div className="space-y-2">
              <Label htmlFor="name">Full Name</Label>
              <Input
                id="name"
                type="text"
                placeholder="Full Name"
                name="name"
                required
              />
            </div>
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
              Sign up
            </Button>
            <Link
              href="/login"
              className="text-sm text-muted-foreground transition duration-150 ease-in-out hover:text-primary"
            >
              Already have an account?
            </Link>
          </CardFooter>
        </form>
      </Card>
    </section>
  );
}
