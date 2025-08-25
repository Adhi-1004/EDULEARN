"use client"

import { useEffect, useRef } from "react"
import Chart from "chart.js/auto"

const PerformanceChart = ({ data }) => {
  const chartRef = useRef(null)
  const chartInstance = useRef(null)

  useEffect(() => {
    if (chartInstance.current) {
      chartInstance.current.destroy()
    }

    const ctx = chartRef.current.getContext("2d")

    chartInstance.current = new Chart(ctx, {
      type: "line",
      data: {
        labels: data.map((_, index) => `Week ${index + 1}`),
        datasets: [
          {
            label: "Performance Score",
            data: data,
            borderColor: "#9333ea", // Purple-600
            backgroundColor: "rgba(147, 51, 234, 0.1)",
            tension: 0.3,
            fill: true,
            pointBackgroundColor: "#9333ea",
            pointBorderColor: "#ffffff",
            pointBorderWidth: 2,
            pointRadius: 5,
            pointHoverRadius: 7,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            backgroundColor: "rgba(255, 255, 255, 0.9)",
            titleColor: "#1f2937",
            bodyColor: "#4b5563",
            borderColor: "#e5e7eb",
            borderWidth: 1,
            padding: 12,
            boxPadding: 6,
            usePointStyle: true,
            callbacks: {
              title: (tooltipItems) => {
                return `Week ${tooltipItems[0].dataIndex + 1}`
              },
              label: (context) => {
                return `Score: ${context.parsed.y}%`
              },
            },
          },
        },
        scales: {
          x: {
            grid: {
              display: false,
            },
            ticks: {
              color: "#6b7280",
            },
          },
          y: {
            beginAtZero: true,
            max: 100,
            ticks: {
              stepSize: 20,
              color: "#6b7280",
            },
            grid: {
              color: "rgba(229, 231, 235, 0.5)",
            },
          },
        },
      },
    })

    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy()
      }
    }
  }, [data])

  return (
    <div className="h-64 w-full">
      <canvas ref={chartRef}></canvas>
    </div>
  )
}

export default PerformanceChart
