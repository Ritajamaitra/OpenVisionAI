import {
  useEffect,
  useState,
} from "react";

import {
  CheckCircle2,
  Image as ImageIcon,
  Loader2,
  Pencil,
} from "lucide-react";

import {
  getDatasetImage,
} from "../../api/annotations";


interface DatasetImageCardProps {

  datasetId: number;

  imageName: string;

  onAnnotate: () => void;
}


export default function DatasetImageCard({
  datasetId,
  imageName,
  onAnnotate,
}: DatasetImageCardProps) {

  const [imageUrl, setImageUrl] =
    useState<string | null>(null);

  const [loading, setLoading] =
    useState(true);


  useEffect(() => {

    let objectUrl:
      string | null = null;

    let mounted = true;


    const load = async () => {

      try {

        const blob =
          await getDatasetImage(
            datasetId,
            imageName
          );


        objectUrl =
          URL.createObjectURL(
            blob
          );


        if (mounted) {

          setImageUrl(
            objectUrl
          );

        }

      } catch {

        if (mounted) {

          setImageUrl(null);

        }

      } finally {

        if (mounted) {

          setLoading(false);

        }

      }

    };


    void load();


    return () => {

      mounted = false;

      if (objectUrl) {

        URL.revokeObjectURL(
          objectUrl
        );

      }

    };

  }, [
    datasetId,
    imageName,
  ]);


  return (

    <article className="dataset-image-card">

      <div className="dataset-image-preview">

        {loading ? (

          <Loader2
            size={22}
            className="spin"
          />

        ) : imageUrl ? (

          <img
            src={imageUrl}
            alt={imageName}
          />

        ) : (

          <ImageIcon
            size={32}
          />

        )}

      </div>


      <div className="dataset-image-card-body">

        <div className="dataset-image-name">

          <strong
            title={imageName}
          >
            {imageName}
          </strong>

        </div>


        <div className="dataset-image-status">

          <CheckCircle2
            size={14}
          />

          Ready for annotation

        </div>


        <button
          type="button"
          className="secondary-button dataset-annotate-button"
          onClick={onAnnotate}
        >

          <Pencil size={15} />

          Annotate

        </button>

      </div>

    </article>

  );
}