import { defineConfig } from "astro/config";
import { unified } from "@astrojs/markdown-remark";
import starlight from "@astrojs/starlight";
import starlightImageZoom from "starlight-image-zoom";
import { starlightBasePath } from "starlight-base-path";
import mermaid from "astro-mermaid";

const site = "https://aws-iot-greengrass-v2-edge-walkthrough.johna.kiwi";
const base = "/";

export default defineConfig({
  site,
  base,
  markdown: {
    processor: unified(),
  },
  integrations: [
    mermaid(),
    starlight({
      title: "Greengrass V2 Edge Walkthrough",
      favicon: "/favicon.svg",
      description:
        "AWS IoT Greengrass V2 greenhouse lab — NUC core, ESP32-S3 zones, LAN closed loop, then AWS wiring via CLI.",
      customCss: [
        "./src/styles/patina-tokens.css",
        "./src/styles/splash-overrides.css",
      ],
      components: {
        ThemeSelect: "./src/components/ThemeSelect.astro",
        Head: "./src/components/Head.astro",
      },
      plugins: [starlightBasePath(), starlightImageZoom()],
      social: [
        {
          icon: "github",
          label: "Source Repository",
          href: "https://github.com/jajera/aws-iot-greengrass-v2-edge-walkthrough",
        },
      ],
      editLink: {
        baseUrl:
          "https://github.com/jajera/aws-iot-greengrass-v2-edge-walkthrough/edit/main/",
      },
      lastUpdated: true,
      pagination: true,
      sidebar: [
        { label: "Home", link: "/" },
        {
          label: "Before you begin",
          items: [
            { label: "Tooling", slug: "tooling" },
            { label: "Prerequisites", slug: "prerequisites" },
            { label: "Concepts", slug: "concepts" },
            { label: "Why Greengrass?", slug: "why-greengrass" },
          ],
        },
        {
          label: "1 · Greenhouse on the LAN",
          items: [
            { label: "1. Identities", slug: "identities" },
            { label: "2. Prepare the core", slug: "prepare-core" },
            { label: "3. Install Nucleus", slug: "nucleus" },
            { label: "4. Local MQTT stack", slug: "mqtt-stack" },
            { label: "5. Associate zones", slug: "associate" },
            { label: "6. Loop component", slug: "loop" },
            { label: "7. Flash zones", slug: "flash" },
            { label: "8. Prove the LAN loop", slug: "prove-lan" },
          ],
        },
        {
          label: "2 · Wire into AWS",
          items: [
            { label: "9. Architecture", slug: "architecture" },
            { label: "10. Deploy from the cloud", slug: "deploy-cloud" },
            { label: "11. Archive telemetry", slug: "archive" },
            { label: "12. Zone state", slug: "zone-state" },
            { label: "13. Raise an alarm", slug: "alarm" },
            { label: "14. Cloud commands", slug: "command" },
            { label: "15. Edge inference", slug: "inference" },
            { label: "16. Teardown", slug: "teardown" },
          ],
        },
        {
          label: "Reference",
          items: [
            { label: "Troubleshooting", slug: "troubleshooting" },
            { label: "AWS docs", slug: "references" },
          ],
        },
      ],
    }),
  ],
});
