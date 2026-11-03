# Session temporal phase1 adaptive learning

Twenty universal hourly hypotheses on all21 instruments. UTC conditions describe signal-bar opening hours; closes confirm and actual fills use the next observed opening. No local-session or DST inference. Fixed costs and2% stop; yearly concentration remains descriptive.

## Round1: Trend-aligned RSI momentum during signal bars opening13-16UTC may continue over the next six observed bars.

Change: Reproduce original fixed-window baseline under frozen campaign engine.

Observed: 2/21 pass; 2/21 positive; 33,606 trades. Median pass 1.9382%/year; median all21 -7.1815%/year. Run `1d94b1b4828a7738de89`. Audit passed.

Post-result lesson: The baseline reproduces two passes, with monthly openings on every instrument. Score rather than opportunity frequency is binding. Test whether the six-bar cap cuts session momentum too early before relocating the UTC window.

## Round2: Momentum confirmed during the same13-16UTC signal window may require a full24observed-bar horizon rather than six bars.

Change: Increase holding cap6→24bars only.

Observed: 4/21 pass; 4/21 positive; 25,280 trades. Median pass 1.1694%/year; median all21 -4.9160%/year. Run `08bcc8ff3c8f9223d2bf`. Audit passed.

Post-result lesson: Extending holding6→24 doubles passing breadth2→4, reduces turnover25%, and improves the median-all loss. All months remain covered. The EMA exit may still cut moves early, so ablate it while holding horizon and entry time fixed.
