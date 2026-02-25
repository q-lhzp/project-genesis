// ---------------------------------------------------------------------------
// Type declarations for OpenClaw SDK compatibility
// ---------------------------------------------------------------------------

// Override AgentToolResult to accept our current return format
// This makes the SDK accept tools that return { content: [...] } without details
declare global {
  interface AgentToolResult<T = unknown> {
    content?: Array<{ type: string; text: string }>;
    details?: Record<string, unknown>;
  }
}

// Allow any return from tool execute functions
type AnyToolExecute = (toolCallId: string, params: any, signal?: AbortSignal, onUpdate?: any) => Promise<any>;

// Override OpenClawPluginApi to include all properties we use
declare module "openclaw/plugin-sdk" {
  interface OpenClawPluginApi {
    registerTool(tool: {
      name: string;
      description: string;
      parameters: any;
      execute: AnyToolExecute;
    }): void;
    on(event: string, handler: (event: any, ctx: any) => Promise<any>): void;
    logger: {
      info(message: string, ...args: any[]): void;
      warn(message: string, ...args: any[]): void;
      error(message: string, ...args: any[]): void;
      debug(message: string, ...args: any[]): void;
    };
    pluginConfig?: any;
    config?: any;
  }
}

export {};
