import { notFound } from "next/navigation";
import {
  ScreenshotTemplate,
  getSample,
  isScreenKey,
  samples,
  screenLabels,
  type ScreenKey
} from "../../sampleTemplates";

type PageProps = {
  params: Promise<{
    sample: string;
    screen: string;
  }>;
};

export function generateStaticParams() {
  return samples.flatMap((sample) =>
    (Object.keys(screenLabels) as ScreenKey[]).map((screen) => ({
      sample: sample.id,
      screen
    }))
  );
}

export default async function DesignSampleScreenPage({ params }: PageProps) {
  const { sample: sampleId, screen } = await params;
  const sample = getSample(sampleId);
  if (!sample || !isScreenKey(screen)) {
    notFound();
  }

  return <ScreenshotTemplate sample={sample} screen={screen} />;
}
