
import matplotlib.pyplot as plt
import random

random.seed(42)

print("✅ Monte Carlo Insurance Simulation Started")

# -----------------------------
# PARAMETERS
# -----------------------------
POPULATION_SIZE = 1000
YEARS = 10
NUM_SIMULATIONS = 5000
CLAIM_AMOUNT = 10000

INITIAL_WEALTH = 100000
MAX_AFFORDABLE_PREMIUM = 4000

LOW_RISK_SHARE = 0.7
HIGH_RISK_SHARE = 0.3

# -----------------------------
# ETHICAL CONSTRAINTS
# -----------------------------
MAX_ACCEPTABLE_LOSS_PROB = 0.01

# -----------------------------
# SCENARIOS
# -----------------------------
PREMIUM_LEVELS = [2000, 2500, 3000]

SICKNESS_SCENARIOS = {
    "low_risk": (0.01, 0.05),
    "high_risk": (0.02, 0.08)
}

# -----------------------------
# MONTE CARLO SIMULATION
# -----------------------------
def run_monte_carlo(premium_per_person, sick_young, sick_old):

    profits = []
    burdens = []
    utilities = []

    for sim in range(NUM_SIMULATIONS):

        ages = []
        risk_types = []

        for i in range(POPULATION_SIZE):
            ages.append(random.randint(20, 60))

            if random.random() < LOW_RISK_SHARE:
                risk_types.append("low")
            else:
                risk_types.append("high")

        total_premiums = 0
        total_claims = 0

        for year in range(YEARS):

            yearly_premiums = POPULATION_SIZE * premium_per_person
            total_premiums += yearly_premiums

            for i in range(POPULATION_SIZE):

                ages[i] += 1

                if ages[i] < 40:
                    sickness_prob = sick_young
                else:
                    sickness_prob = sick_old

                wealth = INITIAL_WEALTH - premium_per_person

                if random.random() < sickness_prob:

                    if premium_per_person <= MAX_AFFORDABLE_PREMIUM:
                        total_claims += CLAIM_AMOUNT
                    else:
                        wealth -= CLAIM_AMOUNT

                if wealth < 0:
                    wealth = 0

                utility = wealth ** 0.5
                utilities.append(utility)

        profit = total_premiums - total_claims
        profits.append(profit)

        if total_claims > 0:
            burden = total_premiums / total_claims
        else:
            burden = float('inf')

        burdens.append(burden)

    return profits, burdens, utilities


# -----------------------------
# RESULTS
# -----------------------------
results = []

for premium in PREMIUM_LEVELS:
    for risk_name, (sy, so) in SICKNESS_SCENARIOS.items():

        profits, burdens, utilities = run_monte_carlo(premium, sy, so)

        avg_profit = sum(profits) / len(profits)
        avg_burden = sum(burdens) / len(burdens)
        avg_welfare = sum(utilities) / len(utilities)

        prob_loss = sum(1 for p in profits if p < 0) / len(profits)

        profits_sorted = sorted(profits)
        var_5 = profits_sorted[int(0.05 * len(profits))]

        ethically_viable = prob_loss <= MAX_ACCEPTABLE_LOSS_PROB

        avg_sickness_rate = (sy + so) / 2
        expected_claim = CLAIM_AMOUNT * avg_sickness_rate * YEARS
        customer_burden = (premium * YEARS) / expected_claim

        results.append({
            "Premium": premium,
            "Risk": risk_name,
            "Avg Profit": avg_profit,
            "Prob Loss": prob_loss,
            "VaR 5%": var_5,
            "Ethically Viable": ethically_viable,
            "Customer Burden": customer_burden,
            "Avg Burden": avg_burden,
            "Avg Welfare": avg_welfare
        })

        # Histogram
        plt.hist(profits, bins=40)
        plt.title(f"Profit Distribution | Premium {premium} | {risk_name}")
        plt.xlabel("Profit")
        plt.ylabel("Frequency")
        plt.savefig(f"results/profit_{premium}_{risk_name}.png", dpi=300)
        plt.clf()


print("\n==== SENSITIVITY ANALYSIS RESULTS ====\n")

for r in results:
    print("------------------------------------------------")
    print(f"Premium Level      : {r['Premium']}")
    print(f"Risk Scenario      : {r['Risk']}")
    print(f"Average Profit     : {int(r['Avg Profit'])}")
    print(f"Probability of Loss: {r['Prob Loss']:.2f}")
    print(f"VaR (Worst 5%)     : {int(r['VaR 5%'])}")
    print(f"Average Welfare    : {r['Avg Welfare']:.2f}")


# -----------------------------
# PROFIT VS FAIRNESS GRAPH
# -----------------------------
profits_plot = []
burdens_plot = []
labels = []

for r in results:
    profits_plot.append(r["Avg Profit"])
    burdens_plot.append(r["Avg Burden"])
    labels.append(f"{r['Premium']} | {r['Risk']}")

plt.scatter(burdens_plot, profits_plot)

for i, label in enumerate(labels):
    plt.annotate(label, (burdens_plot[i], profits_plot[i]))

plt.xlabel("Customer Burden (Premium / Claims)")
plt.ylabel("Average Company Profit")
plt.title("Profit vs Fairness Tradeoff in Insurance Design")
plt.grid(True)
plt.savefig("results/profit_vs_fairness.png", dpi=300)
plt.show()
