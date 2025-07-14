"use client";

import React, { useEffect, useRef, useMemo, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import remarkGfm from 'remark-gfm';
import 'katex/dist/katex.min.css';
import { cn } from '@/lib/utils';
import { Copy, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

// Define code block component props
type CodeBlockProps = {
  node?: any;
  inline?: boolean;
  className?: string;
  children?: React.ReactNode;
  [key: string]: any;
};

// Memoize the components configuration to avoid recreating on every render
const markdownComponents = {
  // Customize heading styles
  h1: ({ node, ...props }: any) => <h1 className="mt-6 mb-4 text-2xl font-bold" {...props} />,
  h2: ({ node, ...props }: any) => <h2 className="mt-5 mb-3 text-xl font-bold" {...props} />,
  h3: ({ node, ...props }: any) => <h3 className="mt-4 mb-2 text-lg font-bold" {...props} />,
  
  // Add special styling for lists
  ul: ({ node, ...props }: any) => <ul className="pl-6 list-disc mb-4" {...props} />,
  ol: ({ node, ...props }: any) => <ol className="pl-6 list-decimal mb-4" {...props} />,
  // eslint-disable-next-line axe/listitem
  li: ({ node, ...props }: any) => <li className="mb-1 text-foreground" {...props} />,
  
  // Paragraph
  p: ({ node, ...props }: any) => <p className="mb-4 text-foreground" {...props} />,
  
  // Code blocks with syntax highlighting
  code: ({ inline, className, children, ...props }: CodeBlockProps) => {
    const [copied, setCopied] = useState(false);

    if (inline) {
      return (
        <code className="px-1 py-0.5 rounded bg-zinc-100 dark:bg-zinc-800 text-zinc-800 dark:text-zinc-100 font-mono text-sm" {...props}>
          {children}
        </code>
      );
    }

    const codeString = String(children).replace(/\n$/, "");

    const handleCopy = async () => {
      await navigator.clipboard.writeText(codeString);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    };

    return (
      <div className="relative group">
        <pre className="p-4 mb-4 overflow-x-auto rounded-lg bg-zinc-100 dark:bg-zinc-800 text-zinc-800 dark:text-zinc-100">
          <code className={cn("font-mono text-sm", className)} {...props}>
            {children}
          </code>
          <div className="absolute bottom-2 right-2">
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 rounded-full"
                    onClick={handleCopy}
                    aria-label="Copy code"
                  >
                    {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Copy code</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        </pre>
      </div>
    );
  },
  
  // Styling for blockquotes
  blockquote: ({ node, ...props }: any) => (
    <blockquote className="pl-4 italic border-l-4 border-primary/50 my-4" {...props} />
  ),
  
  // Styling for tables
  table: ({ node, ...props }: any) => (
    <div className="overflow-x-auto my-6">
      <table className="min-w-full border-collapse" {...props} />
    </div>
  ),
  th: ({ node, ...props }: any) => (
    <th 
      className="px-4 py-2 border bg-muted font-semibold text-left" 
      {...props} 
    />
  ),
  td: ({ node, ...props }: any) => (
    <td 
      className="px-4 py-2 border" 
      {...props} 
    />
  ),
};

// Memoize the plugins array to avoid recreating it on every render
const remarkPlugins = [remarkMath, remarkGfm];
const rehypePlugins = [[rehypeKatex, { strict: false }]] as any;

const MarkdownRenderer: React.FC<MarkdownRendererProps> = React.memo(({ content, className }) => {
  const markdownRef = useRef<HTMLDivElement>(null);

  // Memoize the markdown content to prevent re-rendering on every character change
  const memoizedMarkdown = useMemo(() => {
    return (
      <ReactMarkdown
        remarkPlugins={remarkPlugins}
        rehypePlugins={rehypePlugins}
        components={markdownComponents}
      >
        {content}
      </ReactMarkdown>
    );
  }, [content]);

  // This effect is to handle any custom rendering needs after markdown is processed
  // Using a cleanup ref to avoid processing too frequently during streaming
  useEffect(() => {
    let timeout: NodeJS.Timeout | null = null;
    
    if (markdownRef.current) {
      // Debounce post-processing for streaming content
      timeout = setTimeout(() => {
        // Add any additional post-processing here if needed
      }, 100);
    }
    
    return () => {
      if (timeout) clearTimeout(timeout);
    };
  }, [content]);

  return (
    <div ref={markdownRef} className={cn("prose dark:prose-invert max-w-none text-foreground", className)}>
      {memoizedMarkdown}
    </div>
  );
});

MarkdownRenderer.displayName = 'MarkdownRenderer';

export default MarkdownRenderer; 