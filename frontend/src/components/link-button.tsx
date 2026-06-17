"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { Button, type ButtonProps } from "@/components/ui/button";
import { Loader2 } from "lucide-react";

interface LinkButtonProps extends ButtonProps {
  href: string;
  children: React.ReactNode;
}

export function LinkButton({ href, children, className, ...props }: LinkButtonProps) {
  const [loading, setLoading] = useState(false);
  const pathname = usePathname();

  // Reset loading state when the pathname changes (navigation completed)
  useEffect(() => {
    setLoading(false);
  }, [pathname]);

  return (
    <Link href={href} onClick={() => setLoading(true)}>
      <Button className={className} disabled={loading} {...props}>
        {loading ? (
          <>
            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            Loading…
          </>
        ) : (
          children
        )}
      </Button>
    </Link>
  );
}
