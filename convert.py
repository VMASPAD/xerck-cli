import json
component = """
/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import * as React from "react";
import { createPortal } from "react-dom";
import { cn } from "@/lib/utils";

// Contexto para compartir estado entre componentes
const TooltipContext = React.createContext<{
  open: boolean;
  setOpen: React.Dispatch<React.SetStateAction<boolean>>;
  content: React.RefObject<HTMLDivElement | null>;
  trigger: React.RefObject<HTMLDivElement | null>;
  side?: "top" | "right" | "bottom" | "left";
  align?: "start" | "center" | "end";
  delayDuration?: number;
}>({
  open: false,
  setOpen: () => {},
  content: React.createRef<HTMLDivElement | null>(),
  trigger: React.createRef<HTMLDivElement | null>(),
  side: "top",
  align: "center",
  delayDuration: 300,
});

interface TooltipProviderProps {
  children: React.ReactNode;
  delayDuration?: number;
}

const TooltipProvider = ({ children, delayDuration = 300 }: TooltipProviderProps) => {
  return (
    <React.Fragment>
      {React.Children.map(children, (child) => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child, { delayDuration } as any);
        }
        return child;
      })}
    </React.Fragment>
  );
};

interface TooltipProps {
  children: React.ReactNode;
  open?: boolean;
  defaultOpen?: boolean;
  onOpenChange?: (open: boolean) => void;
  delayDuration?: number;
  side?: "top" | "right" | "bottom" | "left";
  align?: "start" | "center" | "end";
}

const Tooltip = ({
  children,
  open: controlledOpen,
  defaultOpen = false,
  onOpenChange,
  delayDuration = 300,
  side = "top",
  align = "center",
}: TooltipProps) => {
  const [uncontrolledOpen, setUncontrolledOpen] = React.useState(defaultOpen);
  const open = controlledOpen !== undefined ? controlledOpen : uncontrolledOpen;
  const setOpen = React.useCallback((value: boolean | ((prev: boolean) => boolean)) => {
    if (onOpenChange) {
      if (typeof value === "function") {
        onOpenChange(value(open));
      } else {
        onOpenChange(value);
      }
    }
    setUncontrolledOpen(value);
  }, [onOpenChange, open]);

  const triggerRef = React.useRef<HTMLDivElement>(null);
  const contentRef = React.useRef<HTMLDivElement>(null);

  // Handle click outside to close tooltip
  React.useEffect(() => {
    if (!open) return;

    const handleClickOutside = (e: MouseEvent) => {
      if (
        contentRef.current &&
        !contentRef.current.contains(e.target as Node) &&
        triggerRef.current &&
        !triggerRef.current.contains(e.target as Node)
      ) {
        setOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [open, setOpen]);

  const contextValue = React.useMemo(() => ({
    open,
    setOpen,
    content: contentRef,
    trigger: triggerRef,
    side,
    align,
    delayDuration,
  }), [open, setOpen, side, align, delayDuration]);

  return (
    <TooltipContext.Provider value={contextValue}>
      {children}
    </TooltipContext.Provider>
  );
};

interface TooltipTriggerProps {
  children: React.ReactNode;
  asChild?: boolean;
  className?: string;
}

const TooltipTrigger = React.forwardRef<HTMLDivElement, TooltipTriggerProps>(
  ({ children, asChild, className, ...props }, forwardedRef) => {
    const { setOpen, trigger, delayDuration } = React.useContext(TooltipContext);
    const ref = React.useRef<HTMLDivElement>(null);
    const timeoutRef = React.useRef<NodeJS.Timeout | null>(null);

    // Combinar refs
    React.useImperativeHandle(forwardedRef, () => ref.current!, []);
    React.useEffect(() => {
      if (ref.current && trigger.current === null) {
        trigger.current = ref.current;
      }
    }, [trigger, ref]);

    const handleMouseEnter = () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }

      timeoutRef.current = setTimeout(() => {
        setOpen(true);
      }, delayDuration);
    };

    const handleMouseLeave = () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }

      timeoutRef.current = setTimeout(() => {
        setOpen(false);
      }, delayDuration);
    };

    const element = asChild ? React.Children.only(children) : (
      <div className={cn("inline-block", className)} {...props}>{children}</div>
    );

    return React.cloneElement(element as React.ReactElement, {
      ref: (node: HTMLDivElement | null) => {
        if (node) {
          ref.current = node;
          // Manejar refs si el elemento hijo tiene una ref
          const childRef = (element as any).ref;
          if (typeof childRef === "function") childRef(node);
          else if (childRef) childRef.current = node;
        }
      },
      onMouseEnter: handleMouseEnter,
      onMouseLeave: handleMouseLeave,
      onClick: (e: React.MouseEvent) => {
        // Propagar el evento click al elemento original
        if ((element as any).props && (element as any).props.onClick) {
          (element as any).props.onClick(e);
        }
      },
    });
  }
);

TooltipTrigger.displayName = "TooltipTrigger";

interface TooltipContentProps extends React.HTMLAttributes<HTMLDivElement> {
  showArrow?: boolean;
  arrowClassName?: string;
  sideOffset?: number;
  align?: "start" | "center" | "end";
  side?: "top" | "right" | "bottom" | "left";
}

const TooltipContent = React.forwardRef<HTMLDivElement, TooltipContentProps>(
  ({ className, showArrow, arrowClassName, sideOffset = 4, side: propSide, align: propAlign, children, ...props }, forwardedRef) => {
    const { open, content, trigger, side: contextSide, align: contextAlign } = React.useContext(TooltipContext);
    const ref = React.useRef<HTMLDivElement>(null);
    const [position, setPosition] = React.useState({ top: 0, left: 0 });
    const [arrowPosition, setArrowPosition] = React.useState({ top: 0, left: 0 });
    const [mounted, setMounted] = React.useState(false);
    
    const side = propSide || contextSide || "top";
    const align = propAlign || contextAlign || "center";

    // Combinar refs
    React.useImperativeHandle(forwardedRef, () => ref.current!, []);
    React.useEffect(() => {
      if (ref.current && content.current === null) {
        content.current = ref.current;
      }
    }, [content, ref]);

    React.useEffect(() => {
      setMounted(true);
      return () => setMounted(false);
    }, []);

    React.useEffect(() => {
      if (!open || !trigger.current || !ref.current) return;

      const updatePosition = () => {
        if (!trigger.current || !ref.current) return;

        const triggerRect = trigger.current.getBoundingClientRect();
        const tooltipRect = ref.current.getBoundingClientRect();
        
        // Calcular posición base según el lado
        let top = 0;
        let left = 0;

        const triggerCenterX = triggerRect.left + triggerRect.width / 2;
        const triggerCenterY = triggerRect.top + triggerRect.height / 2;

        switch (side) {
          case "top":
            top = triggerRect.top - tooltipRect.height - sideOffset;
            left = triggerCenterX - tooltipRect.width / 2;
            break;
          case "bottom":
            top = triggerRect.bottom + sideOffset;
            left = triggerCenterX - tooltipRect.width / 2;
            break;
          case "left":
            top = triggerCenterY - tooltipRect.height / 2;
            left = triggerRect.left - tooltipRect.width - sideOffset;
            break;
          case "right":
            top = triggerCenterY - tooltipRect.height / 2;
            left = triggerRect.right + sideOffset;
            break;
        }

        // Aplicar alineación
        if ((side === "top" || side === "bottom") && align !== "center") {
          if (align === "start") {
            left = triggerRect.left;
          } else if (align === "end") {
            left = triggerRect.right - tooltipRect.width;
          }
        } else if ((side === "left" || side === "right") && align !== "center") {
          if (align === "start") {
            top = triggerRect.top;
          } else if (align === "end") {
            top = triggerRect.bottom - tooltipRect.height;
          }
        }

        // Calcular posición de la flecha
        let arrowTop = 0;
        let arrowLeft = 0;

        if (side === "top" || side === "bottom") {
          arrowLeft = triggerCenterX - left;
        } else {
          arrowTop = triggerCenterY - top;
        }

        setPosition({ top, left });
        setArrowPosition({ top: arrowTop, left: arrowLeft });
      };

      updatePosition();
      window.addEventListener("resize", updatePosition);
      window.addEventListener("scroll", updatePosition);

      return () => {
        window.removeEventListener("resize", updatePosition);
        window.removeEventListener("scroll", updatePosition);
      };
    }, [open, side, align, sideOffset, trigger]);

    if (!mounted || !open) {
      return null;
    }

    return createPortal(
      <div
        ref={ref}
        style={{
          position: "fixed",
          top: `${position.top}px`,
          left: `${position.left}px`,
          zIndex: 50,
        }}
        className={cn(
          "z-50 overflow-hidden rounded-md border border-slate-200 bg-white px-3 py-1.5 text-sm text-slate-950 shadow-md animate-in fade-in-0 zoom-in-95 data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-50",
          className
        )}
        data-side={side}
        {...props}
      >
        {children}
        {showArrow && (
          <div 
            className={cn("absolute w-3 h-1.5 rotate-45", arrowClassName)}
            style={{
              [side === "top" ? "bottom" : side === "bottom" ? "top" : "top"]: side === "left" || side === "right" ? `${arrowPosition.top}px` : "-4px",
              [side === "left" ? "right" : side === "right" ? "left" : "left"]: side === "top" || side === "bottom" ? `${arrowPosition.left}px` : "-4px",
              background: "inherit",
              borderLeft: side === "right" ? "1px solid var(--slate-200, #e2e8f0)" : "none",
              borderTop: side === "bottom" ? "1px solid var(--slate-200, #e2e8f0)" : "none",
              borderRight: side === "left" ? "1px solid var(--slate-200, #e2e8f0)" : "none",
              borderBottom: side === "top" ? "1px solid var(--slate-200, #e2e8f0)" : "none",
            }}
          />
        )}
      </div>,
      document.body
    );
  }
);

TooltipContent.displayName = "TooltipContent";

export { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider };

""" 

nameArchive = "Tooltip".lower()

def to_string_json(component_code):
    json_data = json.dumps({"component": component_code, "name":nameArchive,"modules":[""]}, indent=4)
    return json_data

if __name__ == "__main__":
    json_output = to_string_json(component)
    print(json_output)

    with open(f"{nameArchive}.json", "w", encoding="utf-8") as f:
        f.write(json_output)